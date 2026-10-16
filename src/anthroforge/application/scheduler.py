"""One publication thread, owned worker inputs, cooperative cancellation."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter as monotonic
from time import sleep
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.metrics import Metrics


class Scheduler:
    def __init__(self, current: Callable[[], Document], workers: int = 2) -> None:
        self.current = current
        self.jobs: list[Job] = []
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="anthroforge")
        self.workers = workers
        self.checkpoint = current()
        self.epoch = 0
        self.errors: list[str] = []
        self.metrics = Metrics()
        self.can_publish: Callable[[Job], bool] = lambda job: True

    @property
    def blocked(self) -> bool:
        return any(job.active and job.writes for job in self.jobs)

    def submit(self, job: Job) -> str:
        if not self.blocked:
            self.checkpoint = self.current()
        for existing in self.jobs:
            if job.key and existing.key == job.key and existing.active:
                self.cancel_job(existing.id, obsolete=True)
        job.origin, job.epoch = self.current().revision, self.epoch
        self.jobs.append(job)
        return job.id

    def cancel_job(self, job_id: str, obsolete: bool = False) -> None:
        job = next(item for item in self.jobs if item.id == job_id)
        if not job.active:
            return
        job.obsolete |= obsolete
        job.cancel_requested = job.cancel_requested or monotonic()
        job.cancel.set()
        self.metrics.observe("cancel_request", monotonic() - job.cancel_requested)
        if job.future is None:
            self._terminal(job, "obsolete" if job.obsolete else "cancelled")
        else:
            job.state, job.progress = "cancelling", "Stopping at a safe checkpoint"

    def invalidate(self, affected: set[str]) -> None:
        for job in self.jobs:
            if job.active and job.outputs.intersection(affected):
                self.cancel_job(job.id, obsolete=True)

    def retry(self, job_id: str) -> Any:
        job = next(item for item in self.jobs if item.id == job_id)
        if job.active or job.retry is None:
            raise ValueError("This calculation cannot be retried in its current state.")
        return job.retry()

    def restore(self, surviving: set[int]) -> list[Job]:
        self.epoch += 1
        removed = []
        for job in self.jobs:
            revision = job.snapshot.revision if job.snapshot else job.origin
            if job.active and (revision not in surviving or job.origin not in surviving):
                self.cancel_job(job.id, obsolete=True)
                removed.append(job)
        return removed

    def tick(self) -> None:
        for job in tuple(self.jobs):
            if (
                job.active
                and job.future is not None
                and job.future.done()
                and self.can_publish(job)
            ):
                self._finish(job)
        self._dispatch()
        self._checkpoint()

    def _dispatch(self) -> None:
        running = [job for job in self.jobs if job.active and job.future is not None]
        reserved = set().union(*(job.outputs for job in running))
        for job in self.queued():
            if len(running) >= self.workers:
                break
            if job.outputs.intersection(reserved):
                continue
            self._start(job)
            if job.active:
                running.append(job)
                reserved.update(job.outputs)

    def queued(self) -> list[Job]:
        return sorted(
            (job for job in self.jobs if job.state == "queued"),
            key=lambda job: (-job.priority, job.created),
        )

    def _start(self, job: Job) -> None:
        job.snapshot, job.started = self.current(), monotonic()
        job.state, job.progress = "preparing", "Preparing owned input"
        try:
            payload = job.prepare(job.snapshot)
            self.metrics.observe("prepare", monotonic() - job.started)
            job.future = self.pool.submit(self._execute, job, payload)
        except Exception as error:
            job.error = str(error)
            self._terminal(job, "failed")

    @staticmethod
    def _execute(job: Job, payload: Any) -> Any:
        if job.cancel.is_set():
            return None
        job.state, job.progress = "running", "Computing"
        return job.execute(payload, job.cancel)

    def _finish(self, job: Job) -> None:
        try:
            if job.cancel.is_set():
                self._terminal(job, "obsolete" if job.obsolete else "cancelled")
                return
            result = job.future.result() if job.future else None
            self._publish(job, result)
            self._terminal(job, "succeeded")
        except Exception as error:
            job.error = str(error)
            self.errors.append(job.error)
            self._terminal(job, "failed")

    def _publish(self, job: Job, result: Any) -> None:
        job.state, job.progress = "publishing", "Publishing complete result"
        started = monotonic()
        try:
            job.publish(result)
        finally:
            self.metrics.observe("publication", monotonic() - started)

    def _terminal(self, job: Job, state: str) -> None:
        job.state, job.finished = state, monotonic()
        if job.cancel_requested:
            self.metrics.observe("cancel_finish", job.finished - job.cancel_requested)
        job.progress = job.error or state.capitalize()
        if job.cleanup is not None:
            job.cleanup(state)

    def _checkpoint(self) -> None:
        running = [j for j in self.jobs if j.active and j.writes and j.snapshot is not None]
        if running:
            earliest = min(running, key=lambda j: j.started)
            if earliest.snapshot is not None:
                self.checkpoint = earliest.snapshot
        elif not self.blocked:
            self.checkpoint = self.current()

    def wait(self, timeout: float | None = None) -> None:
        started = monotonic()
        while any(job.active for job in self.jobs):
            self.tick()
            if timeout is not None and monotonic() - started >= timeout:
                raise TimeoutError("Calculations are still pending.")
            sleep(0.002)

    def close(self) -> None:
        for job in self.jobs:
            if job.active:
                self.cancel_job(job.id)
        self.pool.shutdown(wait=True, cancel_futures=True)
        self.tick()
