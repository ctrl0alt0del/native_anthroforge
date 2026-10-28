"""One cancellable import preparation, using the application's existing task coordinator."""

from dataclasses import dataclass
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import assembly_preparation, assembly_source


@dataclass
class State:
    token: str = ""
    source: Any = None
    candidate: Any = None
    state: str = "idle"
    job: str = ""
    error: str = ""
    document: str = ""


class Assembly:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.source = State()
        self.preparation = State()

    def inspect(self, path: str) -> dict[str, Any]:
        self.cancel()
        self.source = State(str(uuid4()), state="loading", document=str(self.session.document.id))
        self.submit(self.source, partial(inspect, path), "assembly_inspect")
        return self.status()

    def prepare(self, source: str, selected: list[str], **options: Any) -> dict[str, Any]:
        if source != self.source.token or self.source.state != "ready":
            raise ValueError("A successfully inspected source project is required.")
        self.cancel_preparation()
        self.preparation = State(str(uuid4()), state="preparing", document=self.source.document)
        worker = partial(prepare, self.source.source, tuple(selected), options, self.session.engine)
        self.submit(self.preparation, worker, "assembly_prepare")
        return self.status()

    def submit(self, value: State, worker: Any, kind: str) -> None:
        job = self.job(value, worker, kind)
        if kind == "assembly_prepare":
            job.cancel = NativeCancellation(self.session.engine)
        job.cleanup = partial(completed, value, job)
        job.workload = lambda _: Workload(candidates=1)
        value.job = job.id
        self.session.scheduler.submit(job)

    def job(self, value: State, worker: Any, kind: str) -> Job:
        job = Job(
            "Inspect project" if kind.endswith("inspect") else "Prepare anatomy import",
            frozenset(),
            self.capture,
            worker,
            partial(self.publish, value, kind),
            kind=kind,
            writes=False,
            publish_during_edit=True,
        )
        return job

    def capture(self, document: Any) -> Any:
        return document, self.session.resources.snapshot()

    def publish(self, value: State, kind: str, result: Any) -> None:
        if not self.current(value):
            raise ObsoleteInputs("The import session changed.")
        if kind == "assembly_inspect":
            value.source = result
        else:
            result.reads.require(self.session.document)
            value.candidate = result
        value.state = "ready"

    def current(self, value: State) -> bool:
        return (value is self.source or value is self.preparation) and value.document == str(
            self.session.document.id
        )

    def ready(self, token: str) -> Any:
        value = self.preparation
        if token != value.token or value.state != "ready" or value.candidate is None:
            raise ValueError("Wait for the current import preparation to finish.")
        value.candidate.reads.require(self.session.document)
        return value.candidate

    def cancel_preparation(self) -> None:
        if self.preparation.job:
            self.session.scheduler.cancel_job(self.preparation.job, obsolete=True)
        self.preparation = State()

    def cancel(self) -> None:
        self.cancel_preparation()
        if self.source.job:
            self.session.scheduler.cancel_job(self.source.job, obsolete=True)
        self.source = State()

    def status(self) -> dict[str, Any]:
        from .assembly_inspection import describe

        return describe(self)


def completed(value: State, job: Job, terminal: str) -> None:
    if terminal != "succeeded":
        value.state, value.error = terminal, job.error


def inspect(path: str, _: Any, cancel: Any) -> Any:
    return assembly_source.inspect(path, cancel)


def prepare(
    source: Any, selected: Any, options: Any, engine: Any, payload: Any, cancel: Any
) -> Any:
    return assembly_preparation.prepare(source, selected, options, engine, payload, cancel)
