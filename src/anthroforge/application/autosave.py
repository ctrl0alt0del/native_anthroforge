"""Qt-independent periodic recovery capture using the existing task coordinator."""

from collections.abc import Callable
from threading import Event
from time import monotonic
from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Workload

from . import context_saves
from .recovery import RecoveryStore
from .resources import Resources

if TYPE_CHECKING:
    from .session import Session

Capture = tuple[Document, Resources, str]


def committed(session: "Session") -> Document:
    return context_saves.project(session, checkpoints=True)


class Autosave:
    def __init__(
        self,
        store: RecoveryStore,
        notify: Callable[[dict[str, Any]], None] = lambda record: None,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.store, self.notify, self.clock = store, notify, clock
        self.identity: Any = None
        self.interval, self.due = 0, 0.0
        self.last_revision: int | None = None
        self.job: Job | None = None
        self.last: dict[str, Any] = {}
        self.error = ""

    def reset(self) -> None:
        self.identity, self.last_revision = None, None
        self.last, self.error = {}, ""

    def poll(self, session: "Session") -> None:
        self.configure(session)
        if not session.preferences.value.autosave_enabled or self.clock() < self.due:
            return
        if session.waiting_save or self.job is not None:
            return
        snapshot = committed(session)
        if snapshot.revision in (session.saved_revision, self.last_revision):
            return
        self.due = self.clock() + self.interval
        self.submit(session)

    def configure(self, session: "Session") -> None:
        identity = (id(session), str(session.document.id), str(session.path))
        interval = session.preferences.value.autosave_minutes * 60
        if identity != self.identity or interval != self.interval:
            self.due = self.clock() + interval
            self.last_revision = None
        self.identity, self.interval = identity, interval

    def submit(self, session: "Session") -> None:
        job = self.make_job(session)
        job.cleanup = lambda state: self.finished(job, state)
        self.job = job
        try:
            session.scheduler.submit(job)
        except Exception:
            self.job = None
            raise

    def make_job(self, session: "Session") -> Job:
        return Job(
            "Autosave recovery copy",
            frozenset(("@autosave:" + str(session.document.id),)),
            lambda _: self.capture(session),
            self.execute,
            self.completed,
            writes=False,
            priority=-20,
            kind="project_save",
            publish_during_edit=True,
            workload=lambda _: Workload(entities=len(session.document.entities)),
        )

    def capture(self, session: "Session") -> Capture:
        return committed(session), session.resources.snapshot(), str(session.path or "")

    def execute(self, inputs: Capture, cancel: Event) -> dict[str, Any]:
        document, resources, origin = inputs
        return self.store.write(document, resources, origin, cancel)

    def completed(self, record: dict[str, Any]) -> None:
        self.last, self.error = record, record["warning"]
        self.last_revision = record["revision"]
        self.notify(record)

    def finished(self, job: Job, state: str) -> None:
        self.job = None
        if state == "failed":
            self.error = job.error
            self.notify({"error": self.error})
