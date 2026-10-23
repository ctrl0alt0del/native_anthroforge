"""Bounded runtime evidence; never an attachment or scheduling authority."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from anthroforge.core.results import Port
from anthroforge.profiling.spans import measured


@dataclass
class EditEvidence:
    shortcut: str
    revision: int
    ports: frozenset[Port]
    id: str = field(default_factory=lambda: str(uuid4()))
    jobs: set[str] = field(default_factory=set)
    published: set[Port] = field(default_factory=set)
    failures: dict[str, str] = field(default_factory=dict)
    outcome: str = "updating"


class Observation:
    def __init__(self, session: Any) -> None:
        self.session = session
        self.latest: dict[str, EditEvidence] = {}
        self.records: dict[str, EditEvidence] = {}
        self.effects: dict[str, Any] = {}
        self.formulas: dict[str, Any] = {}
        self.active = ""
        self.serial = 0
        self.pruned: tuple[Any, ...] = ()
        self.graph: Any = None
        self.progress: dict[str, Any] = {}

    def begin(self, shortcut: Any) -> None:
        current = self.records.get(self.active)
        if current is None or current.shortcut != shortcut.id:
            current = self.create(shortcut)
        current.outcome = "updating"
        current.failures.clear()
        self.progress.pop(shortcut.id, None)
        self.serial += 1

    def create(self, shortcut: Any) -> EditEvidence:
        from .shortcut_effects import affected

        current = EditEvidence(
            shortcut.id, self.session.document.revision, affected(self.session, shortcut)
        )
        self.latest.pop(shortcut.id, None)
        self.records[current.id] = self.latest[shortcut.id] = current
        self.active = current.id
        return current

    def requested(self, job: Any) -> None:
        if not job.writes:
            return
        scheduler = self.session.scheduler
        parent = scheduler.registry.by_id.get(scheduler.publishing)
        causes = set(parent.causes if parent else ())
        if self.active:
            causes.add(self.active)
        for record in self.latest.values():
            if record.outcome in ("waiting_manual", "waiting_release") and any(
                p.owner in job.outputs for p in record.ports
            ):
                causes.add(record.id)
        job.causes = tuple(sorted(causes & self.records.keys()))

    def event(self, job: Any, phase: str) -> None:
        if phase == "requested":
            self.requested(job)
            return
        for key in job.causes:
            record = self.records.get(key)
            if record is not None:
                observe(record, job, phase)
        self.serial += bool(job.causes)

    def finish_gesture(self, cancelled: bool = False) -> None:
        if cancelled and self.active in self.records:
            self.records[self.active].outcome = "cancelled"
        self.active = ""
        self.prune()

    def restore(self) -> None:
        self.active = ""
        for record in self.records.values():
            record.outcome = "superseded"
        self.formulas.clear()
        self.progress.clear()
        self.serial += 1
        self.prune()

    def prune(self) -> None:
        stamp = (
            id(self.session.document.shortcuts),
            id(self.session.document.driving_shortcuts),
            self.serial,
            self.session.document.revision,
            self.active,
        )
        if stamp == self.pruned:
            return
        self.pruned = stamp
        self.collect()
        self.settle()

    @measured("inspection", lambda owner: owner.session.profiler)
    def settle(self) -> None:
        from .shortcut_progress import inspect

        for key, record in self.latest.items():
            if record.jobs or record.outcome in ("complete", "cancelled", "superseded"):
                continue
            value = inspect(self.session, key)
            self.progress[key] = value
            if record.id != self.active:
                record.outcome = value["state"]

    def collect(self) -> None:
        shortcuts = {
            s.id
            for s in (*self.session.document.shortcuts, *self.session.document.driving_shortcuts)
        }
        self.latest = {k: v for k, v in self.latest.items() if k in shortcuts}
        retained = {v.id for v in self.latest.values()} | {self.active}
        self.records = {k: v for k, v in self.records.items() if k in retained or v.jobs}
        self.effects = {k: v for k, v in self.effects.items() if k in shortcuts}
        ids = self.session.document.formula_index.formulas
        self.formulas = {k: v for k, v in self.formulas.items() if k in ids}
        self.limit_history()

    def limit_history(self) -> None:
        # Active jobs retain causal identity; completed history is a bounded recent window.
        self.latest = dict(list(self.latest.items())[-64:])
        self.progress = {k: v for k, v in self.progress.items() if k in self.latest}
        self.formulas = dict(list(self.formulas.items())[-1024:])
        self.effects = dict(list(self.effects.items())[-8:])


def observe(record: EditEvidence, job: Any, phase: str) -> None:
    if phase in ("submitted", "coalesced"):
        record.jobs.add(job.id)
        record.failures.pop(repr(sorted(job.outputs)), None)
    elif phase == "terminal":
        record.jobs.discard(job.id)
        if job.state == "succeeded":
            record.published.update(job.provides & record.ports)
        elif job.state == "failed":
            record.failures[repr(sorted(job.outputs))] = job.error
        elif job.state == "cancelled":
            record.failures[repr(sorted(job.outputs))] = "Calculation cancelled"
