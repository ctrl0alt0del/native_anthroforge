"""One lifecycle authority; per-task schedulers decide complexity, delay and execution."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter as monotonic
from time import sleep
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job, Restart
from anthroforge.core.metrics import Metrics
from anthroforge.core.results import Port
from anthroforge.profiling import tasks as trace

from .job_registry import JobRegistry
from .task_execution import InlineBudget, completed_future, execute
from .task_schedulers import task_schedulers


class TaskCoordinator:
    def __init__(
        self,
        current: Callable[[], Document],
        workers: int = 2,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self.current, self.clock = current, clock
        self.registry = JobRegistry()
        self.pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="anthroforge")
        self.workers = workers
        self.checkpoint = current()
        self.epoch = 0
        self.errors: list[str] = []
        self.can_publish: Callable[[Job], bool] = lambda job: True
        self._initialize_scheduling(clock)

    def _initialize_scheduling(self, clock: Callable[[], float]) -> None:
        self.profiler: Any = None
        self.metrics = Metrics()
        self.task_schedulers = task_schedulers()
        self.inline_budget = InlineBudget(clock)
        self.coalescing: dict[str, tuple[float, float]] = {}

    @property
    def jobs(self) -> list[Job]:
        return self.registry.history

    @property
    def active_jobs(self) -> tuple[Job, ...]:
        return tuple(self.registry.active.values())

    @property
    def blocked(self) -> bool:
        return any(job.writes for job in self.registry.active.values())

    def submit(self, job: Job) -> str:
        if job.kind not in self.task_schedulers:
            raise ValueError("No task scheduler registered for " + job.kind)
        if not self.blocked:
            self.checkpoint = self.current()
        self._supersede(job)
        job.origin, job.epoch = self.current().revision, self.epoch
        job.queued_since = self.clock() if job.queued_since is None else job.queued_since
        self.registry.add(job)
        trace.event(self.profiler, job, "queued")
        self._admit(job)
        self._checkpoint()
        return job.id

    def _supersede(self, job: Job) -> None:
        previous = self.coalescing.pop(job.key, None)
        if previous and self.clock() <= previous[1]:
            job.queued_since = previous[0]
        for existing in self.registry.matching("key", (job.key,)):
            if job.key and existing.key == job.key and existing.active:
                if existing.queued_since is not None:
                    job.queued_since = min(
                        job.queued_since if job.queued_since is not None else self.clock(),
                        existing.queued_since,
                    )
                self.cancel_job(existing.id, obsolete=True)

    def pending_since(self, outputs: set[str], kind: str) -> float | None:
        pending = (
            job.queued_since
            for job in self.registry.matching("output", outputs)
            if job.active
            and job.kind == kind
            and job.outputs & outputs
            and job.queued_since is not None
        )
        return min(pending, default=None)

    def _admit(self, job: Job) -> None:
        try:
            self._assess(job)
            plan = job.assessment.schedule if job.assessment else None
            assert plan is not None and job.queued_since is not None
            job.ready_at = min(
                self.clock() + plan.delay_ms / 1000, job.queued_since + plan.max_wait_ms / 1000
            )
            busy = self._waiting(job)
            if not busy and self.can_publish(job) and self.inline_budget.permits(job):
                self._start(job)
        except Exception as error:
            self._failed(job, error)

    def _assess(self, job: Job) -> None:
        started = monotonic()
        job.assessment = trace.call(
            self.profiler, job, "assess", self.task_schedulers[job.kind].assess, job, self.current()
        )
        self.metrics.observe("scheduling", monotonic() - started)

    def _waiting(self, job: Job) -> bool:
        return any(
            j is not job
            and j.active
            and (
                bool(j.provides & job.prerequisites)
                or (j.future is not None and bool(j.outputs & job.outputs))
            )
            for j in self.blockers(job)
        )

    def blockers(self, job: Job) -> list[Job]:
        return self.registry.matching("provides", job.prerequisites) + self.registry.matching(
            "output", job.outputs
        )

    def cancel_job(self, job_id: str, obsolete: bool = False) -> None:
        job = self.registry.by_id[job_id]
        if not job.active:
            return
        if obsolete:
            self._remember_coalescing(job)
        job.obsolete |= obsolete
        self._request_cancel(job)
        if job.future is None:
            self._terminal(job, "obsolete" if job.obsolete else "cancelled")
        else:
            job.state, job.progress = "cancelling", "Stopping at a safe checkpoint"

    def _request_cancel(self, job: Job) -> None:
        started = monotonic()
        job.cancel_requested = job.cancel_requested or started
        assert job.cancel is not None
        job.cancel.set()
        trace.event(self.profiler, job, "cancel_requested")
        self.metrics.observe("cancel_request", monotonic() - started)

    def _remember_coalescing(self, job: Job) -> None:
        if job.state != "queued" or not job.key or job.queued_since is None:
            return
        wait = job.assessment.schedule.max_wait_ms if job.assessment else 0
        self.coalescing[job.key] = (job.queued_since, self.clock() + wait / 1000)

    def invalidate(self, affected: set[str]) -> None:
        for job in self.registry.matching("owner", affected):
            if job.active and (job.outputs | job.reads).intersection(affected):
                self.cancel_job(job.id, obsolete=True)

    def invalidate_ports(self, affected: set[Port]) -> None:
        owners = {port.owner for port in affected}
        for job in self.registry.matching("port", affected) + self.registry.matching(
            "legacy", owners
        ):
            reads = job.observes | job.prerequisites | job.provides
            legacy = not reads and bool((job.outputs | job.reads) & owners)
            if job.active and (bool(reads & affected) or legacy):
                self.cancel_job(job.id, obsolete=True)

    def retry(self, job_id: str) -> Any:
        job = self.registry.by_id[job_id]
        if job.active or job.retry is None:
            raise ValueError("This calculation cannot be retried in its current state.")
        return job.retry()

    def restore(self, surviving: set[int]) -> list[Restart]:
        self.epoch += 1
        removed = []
        for job in self.active_jobs:
            revision = job.snapshot.revision if job.snapshot else job.origin
            if job.active and (revision not in surviving or job.origin not in surviving):
                if job.restart_on_redo and job.retry:
                    removed.append(Restart(revision, job.retry))
                self.cancel_job(job.id, obsolete=True)
        return removed

    def tick(self) -> None:
        for job in self.active_jobs:
            if self._finishable(job):
                self._finish(job)
        self._dispatch()
        self._checkpoint()

    def _finishable(self, job: Job) -> bool:
        done = job.future is not None and job.future.done()
        cancelled = job.cancel is not None and job.cancel.is_set()
        return job.active and done and (cancelled or self.can_publish(job))

    def _dispatch(self) -> None:
        running = [job for job in self.active_jobs if job.future is not None]
        reserved = set().union(*(job.outputs for job in running))
        for job in self.queued():
            if len(running) >= self.workers:
                break
            if not self._ready(job, reserved):
                continue
            self._start(job)
            if job.active:
                running.append(job)
                reserved.update(job.outputs)

    def _ready(self, job: Job, reserved: set[str]) -> bool:
        return not (job.outputs & reserved or self.clock() < job.ready_at or self._waiting(job))

    def queued(self) -> list[Job]:
        return sorted(
            (job for job in self.active_jobs if job.state == "queued"),
            key=lambda job: (-(job.priority + 100 * job.interactive), job.created),
        )

    def _start(self, job: Job) -> None:
        job.snapshot, job.started = self.current(), monotonic()
        job.dispatch_revision = job.snapshot.revision
        job.state, job.progress = "preparing", "Preparing owned input"
        try:
            self._assess(job)
            payload = trace.call(self.profiler, job, "prepare", job.prepare, job.snapshot)
            job.prepare_ms = (monotonic() - job.started) * 1000
            self.metrics.observe("prepare", job.prepare_ms / 1000)
            self._execute(job, payload)
        except Exception as error:
            self._failed(job, error)

    def _execute(self, job: Job, payload: Any) -> None:
        if self.can_publish(job) and self.inline_budget.permits(job):
            job.execution = "inline"
            job.future = completed_future(job, payload, self.profiler)
            self._finish(job)
            self.inline_budget.charge(job)
        else:
            job.execution = "worker"
            if job.assessment and job.assessment.schedule.execution == "inline":
                job.execution_reason = (
                    "Shared interactive budget exhausted"
                    if self.can_publish(job)
                    else "Publication deferred by the editing transaction"
                )
            job.future = self.pool.submit(execute, job, payload, self.profiler)

    def _finish(self, job: Job) -> None:
        try:
            assert job.cancel is not None
            if job.cancel.is_set():
                self._terminal(job, "obsolete" if job.obsolete else "cancelled")
                return
            result = job.future.result() if job.future else None
            self._publish(job, result)
            self._terminal(job, "succeeded")
        except Exception as error:
            self._failed(job, error)

    def _failed(self, job: Job, error: Exception) -> None:
        job.error = str(error)
        self.errors.append(job.error)
        self._terminal(job, "failed")

    def _publish(self, job: Job, result: Any) -> None:
        job.state, job.progress = "publishing", "Publishing complete result"
        started = monotonic()
        try:
            trace.call(self.profiler, job, "publish", job.publish, result)
        finally:
            job.publish_ms = (monotonic() - started) * 1000
            self.metrics.observe("publication", job.publish_ms / 1000)

    def _terminal(self, job: Job, state: str) -> None:
        job.state, job.finished = state, monotonic()
        if job.cancel_requested:
            self.metrics.observe("cancel_finish", job.finished - job.cancel_requested)
        job.progress = job.error or state.capitalize()
        self._cleanup(job, state)
        self.task_schedulers[job.kind].observe(job)
        trace.event(self.profiler, job, job.state)
        self.registry.finish(job)

    def _cleanup(self, job: Job, state: str) -> None:
        try:
            if job.cleanup is not None:
                job.cleanup(state)
        except Exception as error:
            job.state, job.error = "failed", str(error)
            job.progress = job.error
            self.errors.append(job.error)

    def _checkpoint(self) -> None:
        running = [j for j in self.active_jobs if j.writes and j.snapshot is not None]
        if running:
            earliest = min(running, key=lambda j: j.started)
            if earliest.snapshot is not None:
                self.checkpoint = earliest.snapshot
        elif not self.blocked:
            self.checkpoint = self.current()

    def wait(self, timeout: float | None = None) -> None:
        started = monotonic()
        while self.registry.active:
            self.tick()
            if timeout is not None and monotonic() - started >= timeout:
                raise TimeoutError("Calculations are still pending.")
            sleep(0.002)

    def close(self) -> None:
        for job in self.active_jobs:
            if job.active:
                self.cancel_job(job.id)
        self.pool.shutdown(wait=True, cancel_futures=True)
        self.tick()
