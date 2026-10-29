"""Job contracts shared by GUI and numerical headless sessions."""

from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import asdict, dataclass, field
from threading import Event
from time import perf_counter as monotonic
from typing import Any
from uuid import uuid4

from .document import Document
from .results import Port
from .scheduling import Assessment, QueueDemand, RequestUrgency, Workload

TERMINAL = frozenset(("succeeded", "failed", "cancelled", "obsolete"))


class ObsoleteInputs(Exception):
    """The owned result is valid for an older read set and must not be published."""


def retired(*args: Any) -> Any:
    raise RuntimeError("Completed job execution data has been released.")


@dataclass(frozen=True, slots=True)
class Restart:
    revision: int
    callback: Callable[[], Any]


@dataclass
class Job:
    label: str
    outputs: frozenset[str]
    prepare: Callable[[Document], Any]
    execute: Callable[[Any, Event], Any]
    publish: Callable[[Any], None]
    key: str = ""
    writes: bool = True
    priority: int = 0
    id: str = field(default_factory=lambda: str(uuid4()))
    state: str = "queued"
    origin: int = 0
    epoch: int = 0
    snapshot: Document | None = None
    dispatch_revision: int | None = None
    future: Future[Any] | None = None
    cancel: Event | None = field(default_factory=Event)
    obsolete: bool = False
    created: float = field(default_factory=monotonic)
    started: float = 0.0
    finished: float = 0.0
    cancel_requested: float = 0.0
    error: str = ""
    progress: str = "Waiting for inputs"
    captures: frozenset[str] = frozenset()
    retry: Callable[[], Any] | None = None
    cleanup: Callable[[str], None] | None = None
    kind: str = "generic"
    context: str = ""
    interactive: bool = False
    workload: Callable[[Document], Workload] = lambda _: Workload()
    assessment: Assessment | None = None
    queued_since: float | None = None
    ready_at: float = 0.0
    execution: str = ""
    execution_reason: str = ""
    prepare_ms: float = 0.0
    compute_ms: float = 0.0
    publish_ms: float = 0.0
    reads: frozenset[str] = frozenset()
    publish_during_edit: bool = False
    restart_on_redo: bool = False
    restart_on_input_change: bool = False
    restart_requested: bool = False
    prerequisites: frozenset[Port] = frozenset()
    provides: frozenset[Port] = frozenset()
    observes: frozenset[Port] = frozenset()
    renew_inputs: Callable[["Job", Document], None] | None = None
    inputs_key: Callable[[Document], Any] | None = None
    accepted_inputs_key: Any = None
    edit_contexts: tuple[str, ...] = ()
    causes: tuple[str, ...] = ()
    urgency: RequestUrgency | None = None
    queue_demand: QueueDemand | None = None

    @property
    def active(self) -> bool:
        return self.state not in TERMINAL

    @property
    def retryable(self) -> bool:
        return self.retry is not None and self.state in ("failed", "cancelled")

    def retire(self) -> None:
        if self.snapshot is not None:
            self.dispatch_revision = self.snapshot.revision
        self.snapshot = self.future = self.cleanup = self.cancel = None
        self.renew_inputs = self.inputs_key = self.accepted_inputs_key = None
        self.prepare = self.execute = self.publish = self.workload = retired
        self.prerequisites = self.provides = self.observes = frozenset()
        self.reads = self.captures = frozenset()
        if not self.retryable:
            self.retry = None

    def describe(self) -> dict[str, Any]:
        end = self.finished or monotonic()
        return {
            "id": self.id,
            "label": self.label,
            "state": self.state,
            "outputs": sorted(self.outputs),
            "error": self.error,
            "elapsed": end - (self.started or self.created),
            "progress": self.progress,
            "obsolete": self.obsolete,
            "writes": self.writes,
            "retryable": self.retryable,
            "scheduling": self.scheduling_details(),
        }

    def scheduling_details(self) -> dict[str, Any]:
        if self.assessment is None:
            return {"kind": self.kind}
        plan = self.assessment.schedule
        return {
            "kind": self.kind,
            "execution": self.execution or plan.execution,
            "estimated_ms": plan.estimated_ms,
            "delay_ms": plan.delay_ms,
            "reason": self.execution_reason or plan.reason,
            "actual_ms": self.prepare_ms + self.compute_ms + self.publish_ms,
            "workload": asdict(self.assessment.workload),
            "resources": asdict(plan.resources),
        }
