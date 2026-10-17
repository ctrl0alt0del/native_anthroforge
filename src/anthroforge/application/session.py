"""The single application API used by UI, CLI, automation and tests."""

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Workspace
from anthroforge.core.jobs import Job
from anthroforge.native.mesh import GeometryEngine
from anthroforge.profiling import RuntimeProfiler
from anthroforge.profiling.spans import measured
from anthroforge.profiling.tasks import command_metadata
from anthroforge.profiling.tasks import operation as profile_operation

from .assets import Asset
from .changes import ChangeJournal
from .coordinator import TaskCoordinator
from .entity_revisions import POSE_FIELDS, changed_ports, differs
from .entity_revisions import authored as authored_entity
from .history import History


class Session:
    def __init__(self, name: str = "Untitled", profiler: RuntimeProfiler | None = None) -> None:
        self.changes, self._document = ChangeJournal(), Document(name=name)
        self.history = History(self.document)
        self.assets: dict[str, Asset] = {}
        self.initialize_runtime(profiler)
        self._engine: GeometryEngine | None = None
        self.serial = 0
        self.path: Path | None = None
        self.file_lock: Any = None
        self.saved_revision = 0
        self.active_workspace = 0
        self.waiting_save = False
        self.replay_callback: Any = None

    def initialize_runtime(self, profiler: RuntimeProfiler | None) -> None:
        self.owns_profiler = profiler is None
        self.profiler = profiler if profiler is not None else RuntimeProfiler()
        self.initialize_scheduler()

    @property
    def document(self) -> Document:
        return self._document

    @document.setter
    def document(self, value: Document) -> None:
        self.changes.record(self._document, value)
        self._document = value

    def initialize_scheduler(self) -> None:
        self.scheduler = TaskCoordinator(lambda: self.document)
        self.scheduler.profiler = self.profiler
        self.scheduler.can_publish = self.can_publish

    @property
    def engine(self) -> GeometryEngine:
        if self._engine is None:
            self._engine = GeometryEngine()
            self.profiler.native.attach(self._engine)
        return self._engine

    def can_publish(self, job: Job) -> bool:
        return self.history.before is None or job.publish_during_edit

    @property
    def workspace(self) -> Workspace:
        return self.document.workspaces[self.active_workspace]

    def priority(self, ids: set[str]) -> int:
        return 10 if not self.workspace.focused or ids.intersection(self.workspace.members) else 0

    def editable(self, entity_id: str) -> SCP:
        if self.waiting_save:
            raise ValueError("Editing is blocked while waiting to save.")
        if self.workspace.focused and entity_id not in self.workspace.members:
            raise ValueError("This SCP is outside the focused workspace and is read-only.")
        return self.document.entity(entity_id)

    def replace_document(self, **changes: Any) -> None:
        self.serial += 1
        self.document = replace(self.document, revision=self.serial, **changes)
        self.history.observe(self.document)

    def replace_entities(self, changed: dict[str, SCP], authored: bool = True) -> None:
        if authored:
            changed = self.authored_entities(changed)
        entities = tuple(
            merge_entity(item, changed.get(item.id, item)) for item in self.document.entities
        )
        self.replace_document(entities=entities)

    def authored_entities(self, changed: dict[str, SCP]) -> dict[str, SCP]:
        ports = set().union(
            *(changed_ports(self.document.entity(key), value) for key, value in changed.items())
        )
        self.scheduler.invalidate_ports(ports)
        return {
            key: authored_entity(self.document.entity(key), value) for key, value in changed.items()
        }

    @measured("transaction", lambda session: session.profiler)
    def begin(self) -> None:
        if self.waiting_save:
            raise ValueError("Editing is blocked while waiting to save.")
        self.history.begin(self.document)

    @measured("transaction", lambda session: session.profiler)
    def commit(self) -> None:
        self.history.commit(self.document, self.replay_callback)
        self.replay_callback = None
        from .operations import released

        released(self)

    @measured("transaction", lambda session: session.profiler)
    def cancel(self) -> None:
        self.document = replace(self.history.cancel(), workspaces=self.document.workspaces)
        self.scheduler.restore(self.history.surviving())
        self.replay_callback = None
        self.resume_calculations()

    @measured("transaction", lambda session: session.profiler)
    def navigate(self, direction: int) -> None:
        if self.waiting_save:
            raise ValueError("History is blocked while waiting to save.")
        previous = self.document
        self.document = replace(self.history.navigate(direction), workspaces=previous.workspaces)
        self.remember_restarts(self.scheduler.restore(self.history.surviving()))
        changed = changed_ids(previous, self.document)
        self.scheduler.invalidate(changed)
        if direction > 0:
            self.history.replay()
        self.resume_calculations()

    def remember_restarts(self, jobs: list[Job]) -> None:
        for job in jobs:
            revision = job.snapshot.revision if job.snapshot else job.origin
            for entry in self.history.entries[self.history.cursor + 1 :]:
                if revision in entry.versions and job.restart_on_redo and job.retry:
                    entry.restarts.append(job.retry)
                    break

    def resume_calculations(self) -> None:
        from . import evaluation
        from .construction_tasks import schedule
        from .control_tasks import resume

        resume(self)
        targets = {e.id for e in self.document.entities if e.status in ("edited", "stale")}
        captures = {e.id for e in self.document.entities if e.status == "edited"}
        if targets and self.document.attachments_enabled and self.document.update_mode != "MANUAL":
            evaluation.request(self, targets, captures)
        schedule(self, {e.id for e in self.document.entities if e.result.status == "pending"})

    def command(self, operation: str, **arguments: Any) -> Any:
        from .commands import execute

        if operation.startswith("profile."):
            return profile_operation(self, operation, arguments)
        return self.profiler.call(
            "command",
            operation,
            execute,
            self,
            operation,
            arguments,
            _metadata=command_metadata(self, arguments),
        )

    def wait(self, timeout: float | None = None) -> None:
        from .geometry_ownership import collect

        self.scheduler.wait(timeout)
        collect(self)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.document.name,
            "id": str(self.document.id),
            "revision": self.document.revision,
            "metres_per_unit": 1.0,
            "entity_count": len(self.document.entities),
            "skin_available": False,
            "entities": [asdict(item) for item in self.document.entities],
            "controls": [asdict(item) for item in self.document.controls],
            "jobs": [job.describe() for job in self.scheduler.jobs],
            "save_blocked": self.scheduler.blocked,
            "checkpoint_revision": self.scheduler.checkpoint.revision,
            "workspace": asdict(self.workspace),
        }

    def close(self) -> None:
        self.scheduler.close()
        if self._engine is not None:
            self.profiler.native.detach(self._engine)
        if self.owns_profiler:
            self.profiler.close()
        if self.file_lock:
            self.file_lock.close()


def changed_ids(previous: Document, current: Document) -> set[str]:
    changed = {e.id for e in previous.entities if e not in current.entities}
    return changed | {c.id for c in previous.controls if c not in current.controls}


def merge_entity(previous: SCP, current: SCP) -> SCP:
    moved = differs(previous, current, POSE_FIELDS)
    return replace(current, pose_revision=previous.pose_revision + 1) if moved else current
