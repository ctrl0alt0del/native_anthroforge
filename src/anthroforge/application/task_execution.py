"""Bounded owner-thread admission and shared worker/inline execution accounting."""

from collections.abc import Callable
from concurrent.futures import Future
from time import perf_counter
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.profiling import tasks as trace

from .task_schedulers import INLINE_BUDGET_MS, INLINE_WINDOW_MS


class InlineBudget:
    def __init__(self, clock: Callable[[], float]) -> None:
        self.clock = clock
        self.started = clock()
        self.spent_ms = 0.0

    def permits(self, job: Job) -> bool:
        now = self.clock()
        if (now - self.started) * 1000 >= INLINE_WINDOW_MS:
            self.started, self.spent_ms = now, 0.0
        plan = job.assessment.schedule if job.assessment else None
        return bool(
            plan
            and plan.execution == "inline"
            and plan.estimated_ms is not None
            and self.spent_ms + plan.estimated_ms <= INLINE_BUDGET_MS
        )

    def charge(self, job: Job) -> None:
        self.spent_ms += job.prepare_ms + job.compute_ms + job.publish_ms


def execute(job: Job, payload: Any, profiler: Any = None) -> Any:
    started = perf_counter()
    try:
        assert job.cancel is not None
        if job.cancel.is_set():
            return None
        job.state, job.progress = "running", "Computing"
        trace.event(profiler, job, "running")
        return trace.call(profiler, job, "execute", job.execute, payload, job.cancel)
    finally:
        job.compute_ms = (perf_counter() - started) * 1000


def completed_future(job: Job, payload: Any, profiler: Any = None) -> Future[Any]:
    future: Future[Any] = Future()
    try:
        future.set_result(execute(job, payload, profiler))
    except Exception as error:
        future.set_exception(error)
    return future
