"""Job contracts shared by GUI and numerical headless sessions."""

from collections.abc import Callable
from concurrent.futures import Future
from dataclasses import dataclass, field
from threading import Event
from time import perf_counter as monotonic
from typing import Any
from uuid import uuid4

from .document import Document

TERMINAL = frozenset(("succeeded", "failed", "cancelled", "obsolete"))


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
    future: Future[Any] | None = None
    cancel: Event = field(default_factory=Event)
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

    @property
    def active(self) -> bool:
        return self.state not in TERMINAL

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
            "retryable": self.retry is not None and self.state in ("failed", "cancelled"),
        }
