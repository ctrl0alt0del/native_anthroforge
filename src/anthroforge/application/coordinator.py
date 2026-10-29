"""One lifecycle authority; per-task schedulers decide complexity, delay and execution."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter as monotonic
from time import sleep
from typing import Any, cast

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job, ObsoleteInputs, Restart
from anthroforge.core.metrics import Metrics
from anthroforge.core.results import Port
from anthroforge.profiling import causes
from anthroforge.profiling import tasks as trace

from . import (
    external_references,
    scheduling_context,
    task_coalescing,
    task_priorities,
    task_resources,
)
from .job_registry import JobRegistry
from .scheduling_context import SchedulingField
from .task_execution import InlineBudget, completed_future, execute
from .task_schedulers import task_schedulers


def create_executor(workers: int, factory: Any) -> Any:
    return (
        factory()
        if factory is not None
        else ThreadPoolExecutor(max_workers=workers, thread_name_prefix="anthroforge")
    )


class TaskCoordinator:
    context: str
    scheduling_contexts: dict[str, scheduling_context.SchedulingContext]
    context_scope: Any
    registry = SchedulingField[JobRegistry]("registry")
    checkpoint = SchedulingField[Document]("checkpoint")
    epoch = SchedulingField[int]("epoch")
    coalescing = SchedulingField[dict[str, Any]]("coalescing")
    priorities = SchedulingField[task_priorities.TaskPriorities]("priorities")
    publishing = SchedulingField[str]("publishing")
    publication_contexts = SchedulingField[tuple[str, ...]]("publication_contexts")
    annotate = SchedulingField[Any]("annotate")
    before_dispatch = SchedulingField[Any]("before_dispatch")
    observer = SchedulingField[Any]("observer")

    def __init__(
        self,
        current: Callable[[], Document],
        workers: int = 2,
        clock: Callable[[], float] = monotonic,
        executor_factory: Any = None,
    ) -> None:
        self.current, self.clock = current, clock
        scheduling_context.initialize(self, current())
        self.pool = create_executor(workers, executor_factory)
        self.workers = workers
        self.errors: list[str] = []
        self._initialize_scheduling(clock)

    def _initialize_scheduling(self, clock: Callable[[], float]) -> None:
        self._initialize_callbacks()
        self.profiler: Any = None
        self.metrics = Metrics()
        self.task_schedulers = task_schedulers()
        self.inline_budget = InlineBudget(clock)
        self.coalescing = {}
        self.priorities = task_priorities.TaskPriorities()
        self.publishing = ""
        self.publication_contexts = ()
        self.annotate = lambda job, document: None
        self.before_dispatch = lambda job, document: None
        self.admission = task_resources.Admission()

    def _initialize_callbacks(self) -> None:
        self.can_publish: Callable[[Job], bool] = lambda job: True
        self.service_tick: Callable[[], None] = lambda: None
        self.lifecycle: Callable[[Job, str], None] = lambda job, phase: None
        self.observer = lambda job, phase: None

    @property
    def jobs(self) -> list[Job]:
        return self.registry.history

    @property
    def active_jobs(self) -> tuple[Job, ...]:
        return tuple(self.registry.active.values())

    @property
    def all_active_jobs(self) -> tuple[Job, ...]:
        return scheduling_context.all_active(self)

    @property
    def blocked(self) -> bool:
        return any(job.writes for job in self.registry.active.values())

    def submit(self, job: Job) -> str:
        job.context = self.context
        self.annotate(job, self.current())
        self.observer(job, "requested")
        self.priorities.capture(job, self.clock())
        return task_coalescing.reuse(self, job) or self._submit(job)

    def _submit(self, job: Job) -> str:
        if job.kind not in self.task_schedulers:
            raise ValueError("No task scheduler registered for " + job.kind)
        if not self.blocked:
            self.checkpoint = self.current()
        self._supersede(job)
        job.origin, job.epoch = self.current().revision, self.epoch
        job.queued_since = self.clock() if job.queued_since is None else job.queued_since
        self.registry.add(job)
        self.lifecycle(job, "submitted")
        self.observer(job, "submitted")
        trace.event(self.profiler, job, "queued")
        self._admit(job)
        self._checkpoint()
        return job.id

    def sample_resources(self) -> None:
        if self.profiler is not None and self.profiler.active:
            self.profiler.resources.sample()

    def _supersede(self, job: Job) -> None:
        previous = self.coalescing.pop(job.key, None)
        if previous and self.clock() <= previous[1]:
            job.queued_since = previous[0]
            task_priorities.merge(job, previous[2])
        for existing in self.registry.matching("key", (job.key,)):
            if job.key and existing.active and existing.id != self.publishing:
                self._supersede_previous(existing, job)

    def _supersede_previous(self, existing: Job, job: Job) -> None:
        task_priorities.merge(job, existing.urgency)
        if existing.queued_since is not None:
            job.queued_since = min(
                job.queued_since if job.queued_since is not None else self.clock(),
                existing.queued_since,
            )
        self.cancel_job(existing.id, obsolete=True, reason="newer_request", replacement=job.id)

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

    def cancel_job(
        self,
        job_id: str,
        obsolete: bool = False,
        reason: str = "explicit_cancel",
        replacement: str = "",
        restart: bool = False,
    ) -> None:
        job = self.registry.by_id[job_id]
        if not job.active:
            return
        job.restart_requested = restart and job.restart_on_input_change and job.retry is not None
        causes.cancellation(self, job, reason, replacement)
        self._cancel_active(job, obsolete)

    def _cancel_active(self, job: Job, obsolete: bool) -> None:
        if obsolete:
            self._remember_coalescing(job)
        job.obsolete |= obsolete
        self._request_cancel(job)
        if job.future is None and not job.restart_requested:
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
        self.coalescing[job.key] = (job.queued_since, self.clock() + wait / 1000, job.urgency)

    def invalidate(self, affected: set[str], reason: str = "input_owner_changed") -> None:
        causes.invalidated(self, affected, reason)
        for job in self.registry.matching("owner", affected):
            if job.active and (job.outputs | job.reads).intersection(affected):
                self._invalidate_input(job, reason)

    def invalidate_ports(
        self, affected: set[Port], reason: str = "input_output_changed", source: str = ""
    ) -> None:
        causes.invalidated(self, affected, reason, ports=True)
        owners = {port.owner for port in affected}
        for job in self.registry.matching("port", affected) + self.registry.matching(
            "legacy", owners
        ):
            reads = job.observes | job.prerequisites | job.provides
            legacy = not reads and bool((job.outputs | job.reads) & owners)
            if job.id != source and job.active and (bool(reads & affected) or legacy):
                self._invalidate_input(job, reason)

    def _invalidate_input(self, job: Job, reason: str) -> None:
        if job.id == self.publishing:
            return
        if task_coalescing.renewable(job):
            trace.event(self.profiler, job, "inputs_pending")
            return
        self.cancel_job(job.id, obsolete=True, reason=reason, restart=True)

    def retry(self, job_id: str) -> Any:
        job = self.registry.by_id[job_id]
        if job.active or job.retry is None:
            raise ValueError("This calculation cannot be retried in its current state.")
        return self.run_retry(job)

    def run_retry(self, job: Job) -> Any:
        self.observer(job, "retry_begin")
        try:
            return job.retry() if job.retry else None
        finally:
            self.observer(job, "retry_end")

    def restore(self, surviving: set[int]) -> list[Restart]:
        self.epoch += 1
        removed = []
        for job in self.active_jobs:
            revision = job.snapshot.revision if job.snapshot else job.origin
            if job.active and (revision not in surviving or job.origin not in surviving):
                if job.restart_on_redo and job.retry:
                    removed.append(Restart(revision, job.retry))
                self.cancel_job(job.id, obsolete=True, reason="history_revision_removed")
        return removed

    def tick(self) -> None:
        scheduling_context.tick(self)

    def tick_context(self) -> None:
        for job in self.active_jobs:
            if self._finishable(job):
                self._finish(job)
        self._dispatch()
        self._checkpoint()

    def _finishable(self, job: Job) -> bool:
        done = job.future.done() if job.future else job.restart_requested
        cancelled = job.cancel is not None and job.cancel.is_set()
        return job.active and done and (cancelled or self.can_publish(job))

    def _dispatch(self) -> None:
        running = [job for job in scheduling_context.all_active(self) if job.future is not None]
        if len(running) >= self.workers:
            return
        reserved = set().union(*(j.outputs for j in running if j.context == self.context))
        for job in self.queued():
            if len(running) >= self.workers:
                break
            if not self._ready(job, reserved):
                continue
            self._start(job)
            if job.active and job.future is not None:
                running.append(job)
                reserved.update(job.outputs)

    def _ready(self, job: Job, reserved: set[str]) -> bool:
        return self._refresh_pending(job) and not (
            job.outputs & reserved or self.clock() < job.ready_at or self._waiting(job)
        )

    def _refresh_pending(self, job: Job) -> bool:
        try:
            if (
                job.renew_inputs is not None
                and job.inputs_key is not None
                and (job.accepted_inputs_key != job.inputs_key(self.current()))
            ):
                refresh = job.renew_inputs
                self.registry.update(job, lambda: self._renew(job, refresh))
            return True
        except Exception as error:
            self._failed(job, error)
            return False

    def _renew(self, job: Job, refresh: Callable[[Job, Document], None]) -> None:
        refresh(job, self.current())
        self.annotate(job, self.current())

    def queued(self) -> list[Job]:
        if self.profiler is not None and self.profiler.active:
            result = self.profiler.call(
                "scheduler",
                "prioritize",
                self.priorities.ordered,
                self.registry,
                _metadata={"active_jobs": len(self.registry.active)},
            )
            return cast(list[Job], result)
        return self.priorities.ordered(self.registry)

    def _start(self, job: Job) -> None:
        try:
            self._assess(job)
            if self._resources_ready(job):
                self._prepare(job)
        except Exception as error:
            self._failed(job, error)

    def _resources_ready(self, job: Job) -> bool:
        inline = self.can_publish(job) and self.inline_budget.permits(job)
        reason = "" if inline else self.admission.waiting(job, scheduling_context.all_active(self))
        if reason != job.execution_reason:
            job.execution_reason = reason
            if reason:
                trace.event(self.profiler, job, "resource_wait")
        return not reason

    def _prepare(self, job: Job) -> None:
        job.snapshot, job.started = self.current(), monotonic()
        job.dispatch_revision = job.snapshot.revision
        job.state, job.progress = "preparing", "Preparing owned input"
        external_references.require_inputs(job.snapshot, job.observes | job.prerequisites)
        self.before_dispatch(job, job.snapshot)
        payload = trace.call(self.profiler, job, "prepare", job.prepare, job.snapshot)
        job.prepare_ms = (monotonic() - job.started) * 1000
        self.metrics.observe("prepare", job.prepare_ms / 1000)
        self._execute(job, payload)

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
            self.priorities.call(job, self._publish, job, result)
            self._terminal(job, "succeeded")
        except ObsoleteInputs:
            self.cancel_job(job.id, obsolete=True, reason="read_set_changed", restart=True)
            self._terminal(job, "obsolete")
        except Exception as error:
            self._failed(job, error)

    def _failed(self, job: Job, error: Exception) -> None:
        job.error = str(error)
        self.errors.append(job.error)
        self._terminal(job, "failed")

    def _publish(self, job: Job, result: Any) -> None:
        job.state, job.progress = "publishing", "Publishing complete result"
        previous, self.publishing = self.publishing, job.id
        contexts, self.publication_contexts = self.publication_contexts, job.edit_contexts
        started = monotonic()
        try:
            trace.call(self.profiler, job, "publish", job.publish, result)
        finally:
            self.publishing = previous
            self.publication_contexts = contexts
            job.publish_ms = (monotonic() - started) * 1000
            self.metrics.observe("publication", job.publish_ms / 1000)

    def _terminal(self, job: Job, state: str) -> None:
        job.state, job.finished = state, monotonic()
        if job.cancel_requested:
            self.metrics.observe("cancel_finish", job.finished - job.cancel_requested)
        job.progress = job.error or state.capitalize()
        self.priorities.call(job, self._cleanup, job, state)
        self.task_schedulers[job.kind].observe(job)
        trace.event(self.profiler, job, job.state)
        self.lifecycle(job, "terminal")
        self.observer(job, "terminal")
        self.registry.finish(job)

    def _cleanup(self, job: Job, state: str) -> None:
        try:
            if job.cleanup is not None:
                job.cleanup(state)
            if job.restart_requested and state == "obsolete" and job.retry:
                self.run_retry(job)
        except Exception as error:
            job.state, job.error = "failed", str(error)
            job.obsolete = False
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

    def wait(self, timeout: float | None = None, writes_only: bool = False) -> None:
        started = monotonic()
        self.tick()
        while scheduling_context.pending(self, writes_only):
            self.tick()
            if timeout is not None and monotonic() - started >= timeout:
                raise TimeoutError("Calculations are still pending.")
            sleep(0.002)

    def close(self) -> None:
        scheduling_context.close(self)
