"""Run captured sessions on the coordinator's reserved worker, without a nested pool."""

from concurrent.futures import Future
from threading import Event
from typing import Any


class ChildCancellation(Event):
    def __init__(self, parent: Any) -> None:
        super().__init__()
        self.parent, self.handle = parent, parent.handle

    def is_set(self) -> bool:
        return super().is_set() or bool(self.parent.is_set())


class WorkerExecutor:
    def __init__(self, cancel: Any) -> None:
        self.cancel, self.closed = cancel, False

    def submit(self, function: Any, job: Any, *args: Any) -> Future[Any]:
        if self.closed:
            raise RuntimeError("Isolated execution has closed.")
        future: Future[Any] = Future()
        job.cancel = ChildCancellation(self.cancel)
        try:
            future.set_result(function(job, *args))
        except BaseException as error:
            future.set_exception(error)
        return future

    def shutdown(self, wait: bool = True, cancel_futures: bool = False) -> None:
        self.closed = True


def create(document: Any, resources: Any, preferences: Any, cancel: Any) -> Any:
    from .history import History
    from .preferences import PreferenceStore
    from .session import Session

    store = PreferenceStore()
    store.value = preferences
    session = Session(preferences=store, executor_factory=lambda: WorkerExecutor(cancel))
    session.document, session.resources = document, resources.snapshot()
    session.history = History(document)
    session.serial, session.scheduler.checkpoint = document.revision, document
    return session


def settle(session: Any, cancel: Any) -> None:
    from time import sleep

    while session.scheduler.active_jobs:
        if cancel.is_set():
            raise ValueError("Calculation cancelled.")
        session.scheduler.tick()
        sleep(0.002)
    failed = [j for j in session.scheduler.jobs if j.state == "failed"]
    if failed:
        raise ValueError(failed[-1].error)
