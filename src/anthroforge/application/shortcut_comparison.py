"""Session-only baseline and asynchronous comparisons, independent of authored state."""

from dataclasses import dataclass
from time import monotonic, sleep
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import comparison_geometry, shortcut_inspection
from .comparison_journal import Journal
from .inspection import issue_records
from .inspection_context import InspectionContext, freeze, scene_signature


@dataclass(frozen=True)
class Baseline:
    id: str
    shortcut: str
    source: InspectionContext
    evidence: dict[str, Any]
    provisional: bool
    issues: dict[str, Any]


class Comparison:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.baseline: Baseline | None = None
        self.journal = Journal()
        self.job: Job | None = None
        self.result: dict[str, Any] = {}
        self.stamp: Any = None
        self.serial = 0

    def clear(self) -> None:
        if self.job and self.job.active:
            self.session.scheduler.cancel_job(self.job.id, obsolete=True)
        self.baseline, self.job, self.stamp = None, None, None
        self.result = {}
        self.journal = Journal()
        self.serial += 1

    def capture(self, shortcut: str) -> None:
        value = make_baseline(self.session, shortcut)
        active = any(job.writes for job in self.session.scheduler.active_jobs)
        self.clear()
        self.baseline = value
        if active:
            self.journal.invalidate("Calculations were already running at baseline capture.")
        if value.provisional:
            self.journal.invalidate("Baseline captured inside an unfinished gesture.")

    def signature(self) -> Any:
        return (self.baseline.id if self.baseline else "", scene_signature(self.session.document))

    def refresh(self) -> None:
        if self.baseline is None or self.stamp == self.signature():
            return
        if self.job and self.job.active:
            self.session.scheduler.cancel_job(self.job.id, obsolete=True)
        self.stamp = self.signature()
        self.job = create_job(self, self.stamp)
        self.session.scheduler.submit(self.job)

    def publish(self, stamp: Any, result: Any) -> None:
        if stamp == self.signature():
            self.result = result
            self.serial += 1


def evidence(session: Any, shortcut: str) -> dict[str, Any]:
    return {
        name: operation(session, shortcut)
        for name, operation in shortcut_inspection.operations().items()
        if name
        in (
            "shortcut.effects",
            "shortcut.formulas",
            "shortcut.attachment_policy",
            "shortcut.progress",
        )
    }


def make_baseline(session: Any, shortcut: str) -> Baseline:
    return Baseline(
        str(uuid4()),
        shortcut,
        freeze(session),
        evidence(session, shortcut),
        session.history.before is not None,
        issue_records(session),
    )


def create_job(state: Comparison, stamp: Any) -> Job:
    before, current = state.baseline, freeze(state.session)
    assert before is not None
    job = Job(
        "Compare shortcut baseline",
        frozenset(),
        lambda _: (before.source, current),
        compute,
        lambda result: state.publish(stamp, result),
        writes=False,
        publish_during_edit=True,
        kind="tissue_inspection",
    )
    return configure_job(state, current, job)


def configure_job(state: Comparison, current: Any, job: Job) -> Job:
    job.priority, job.key = -5, "shortcut_comparison"
    job.cancel = NativeCancellation(state.session.engine)
    job.workload = lambda _: workload(current)
    return job


def workload(context: Any) -> Workload:
    meshes, paths = context.resources.meshes.values(), context.resources.paths.values()
    return Workload(
        affected=len(context.document.registry.records),
        triangles=sum(asset.mesh.counts[3] for asset in meshes),
        candidates=sum(asset.path.count for asset in paths),
    )


def compute(pair: Any, token: Any) -> Any:
    return comparison_geometry.compare(pair[0], pair[1], token.handle)


def capture(session: Any, shortcut: str) -> dict[str, Any]:
    session.shortcut_comparison.capture(shortcut)
    return inspect(session)


def clear(session: Any) -> dict[str, Any]:
    session.shortcut_comparison.clear()
    return inspect(session)


def inspect(session: Any, refresh: bool = False, wait: bool = False) -> dict[str, Any]:
    state = session.shortcut_comparison
    if refresh or wait:
        state.refresh()
    if wait and state.job:
        wait_for(session.scheduler, state.job)
    return describe(state)


def wait_for(scheduler: Any, job: Job, timeout: float = 120) -> None:
    started = monotonic()
    while job.active:
        scheduler.tick()
        if monotonic() - started >= timeout:
            raise TimeoutError("Comparison is still pending.")
        sleep(0.002)


def describe(state: Comparison) -> dict[str, Any]:
    baseline = state.baseline
    return dict(
        active=baseline is not None,
        id=baseline.id if baseline else "",
        baseline_revision=baseline.source.document.revision if baseline else None,
        provisional=baseline.provisional if baseline else False,
        replay=state.journal.describe(),
        comparison=state.result,
        state=job_state(state),
        serial=state.serial,
        error=state.job.error if state.job else "",
    )


def job_state(state: Comparison) -> str:
    if not state.baseline:
        return "empty"
    if state.stamp != state.signature():
        return "stale" if state.result else "uncalculated"
    return state.job.state if state.job else "idle"
