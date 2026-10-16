"""The single application API used by UI, CLI, automation and tests."""

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Workspace
from anthroforge.core.jobs import Job
from anthroforge.native.mesh import GeometryEngine

from .assets import Asset
from .history import History
from .scheduler import Scheduler


class Session:
    def __init__(self, name: str = "Untitled") -> None:
        self.document = Document(name=name)
        self.history = History(self.document)
        self.assets: dict[str, Asset] = {}
        self.scheduler = Scheduler(lambda: self.document)
        self.scheduler.can_publish = self.can_publish
        self._engine: GeometryEngine | None = None
        self.serial = 0
        self.path: Path | None = None
        self.file_lock: Any = None
        self.saved_revision = 0
        self.active_workspace = 0
        self.waiting_save = False
        self.replay_callback: Any = None

    @property
    def engine(self) -> GeometryEngine:
        if self._engine is None:
            self._engine = GeometryEngine()
        return self._engine

    def can_publish(self, job: Job) -> bool:
        return self.history.before is None or job.key.startswith("attachments:")

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
            self.scheduler.invalidate(set(changed))
            changed = {
                key: replace(value, generation=value.generation + 1)
                for key, value in changed.items()
            }
        entities = tuple(changed.get(item.id, item) for item in self.document.entities)
        self.replace_document(entities=entities)

    def begin(self) -> None:
        if self.waiting_save:
            raise ValueError("Editing is blocked while waiting to save.")
        self.history.begin(self.document)

    def commit(self) -> None:
        self.history.commit(self.document, self.replay_callback)
        self.replay_callback = None
        from .operations import released

        released(self)

    def cancel(self) -> None:
        self.document = replace(self.history.cancel(), workspaces=self.document.workspaces)
        self.scheduler.restore(self.history.surviving())
        self.replay_callback = None
        self.resume_calculations()

    def navigate(self, direction: int) -> None:
        if self.waiting_save:
            raise ValueError("History is blocked while waiting to save.")
        previous = self.document
        self.document = replace(self.history.navigate(direction), workspaces=previous.workspaces)
        self.remember_restarts(self.scheduler.restore(self.history.surviving()))
        changed = {e.id for e in previous.entities if e not in self.document.entities}
        self.scheduler.invalidate(changed)
        if direction > 0:
            self.history.replay()
        self.resume_calculations()

    def remember_restarts(self, jobs: list[Job]) -> None:
        for job in jobs:
            revision = job.snapshot.revision if job.snapshot else job.origin
            for entry in self.history.entries[self.history.cursor + 1 :]:
                if revision in entry.versions and job.key.startswith("attachments:") and job.retry:
                    entry.restarts.append(job.retry)
                    break

    def resume_calculations(self) -> None:
        from . import evaluation

        targets = {e.id for e in self.document.entities if e.status in ("edited", "stale")}
        captures = {e.id for e in self.document.entities if e.status == "edited"}
        if targets and self.document.attachments_enabled and self.document.update_mode != "MANUAL":
            evaluation.request(self, targets, captures)

    def command(self, operation: str, **arguments: Any) -> Any:
        from .commands import execute

        return execute(self, operation, arguments)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.document.name,
            "id": str(self.document.id),
            "revision": self.document.revision,
            "metres_per_unit": 1.0,
            "entity_count": len(self.document.entities),
            "skin_available": False,
            "entities": [asdict(item) for item in self.document.entities],
            "jobs": [job.describe() for job in self.scheduler.jobs],
            "save_blocked": self.scheduler.blocked,
            "checkpoint_revision": self.scheduler.checkpoint.revision,
            "workspace": asdict(self.workspace),
        }

    def close(self) -> None:
        self.scheduler.close()
        if self.file_lock:
            self.file_lock.close()
