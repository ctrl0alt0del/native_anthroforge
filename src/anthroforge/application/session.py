"""The single application API used by UI, CLI, automation and tests."""

from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Workspace
from anthroforge.core.jobs import Job, Restart
from anthroforge.core.results import Port
from anthroforge.native.mesh import GeometryEngine
from anthroforge.profiling import RuntimeProfiler, causes
from anthroforge.profiling.spans import measured
from anthroforge.profiling.tasks import command_metadata
from anthroforge.profiling.tasks import operation as profile_operation

from .assets import Asset
from .changes import ChangeJournal
from .coordinator import TaskCoordinator
from .curve_conversion import ConversionPreview
from .document_relationships import retain_settings
from .entity_revisions import POSE_FIELDS, changed_ports, differs
from .entity_revisions import authored as authored_entity
from .history import History
from .mirror_policy import require_transition as require_mirror_transition
from .preferences import PreferenceStore, load_user_preferences
from .previews import Preview
from .resources import Resources
from .surface_preview import Candidate
from .tissue_preview import Candidate as TissueCandidate


class Session:
    def __init__(
        self,
        name: str = "Untitled",
        profiler: RuntimeProfiler | None = None,
        preferences: PreferenceStore | None = None,
        executor_factory: Any = None,
    ) -> None:
        self.initialize_document(name, executor_factory)
        self.preferences = preferences if preferences is not None else load_user_preferences()
        self.initialize_runtime(profiler)
        self._engine: GeometryEngine | None = None
        self.initialize_file_state()

    def initialize_document(self, name: str, executor_factory: Any) -> None:
        from .geometry_ownership import Reachability

        self.changes, self._document = ChangeJournal(), Document(name=name)
        self.history = History(self.document)
        self.resources = Resources()
        self.reachability = Reachability()
        self.executor_factory = executor_factory

    def initialize_file_state(self) -> None:
        self.serial = 0
        self.path: Path | None = None
        self.file_lock: Any = None
        self.saved_revision = 0
        self.formula_write_authority: frozenset[str] = frozenset()
        self.formula_observing = False
        self.active_workspace = 0
        self.waiting_save = False
        self.replay_callback: Any = None

    def initialize_runtime(self, profiler: RuntimeProfiler | None) -> None:
        from .issues.repairs import register
        from .issues.system import IssueSystem
        from .skin_status import SkinStatusProvider

        self.owns_profiler = profiler is None
        self.profiler = profiler if profiler is not None else RuntimeProfiler()
        self.profiler.resources.sessions.add(self)
        self.initialize_scheduler()
        self.issues = IssueSystem(self)
        self.skin_status = SkinStatusProvider(self)
        register(self)

    @property
    def assets(self) -> dict[str, Asset]:
        return self.resources.meshes

    @property
    def document(self) -> Document:
        return self._document

    @document.setter
    def document(self, value: Document) -> None:
        self.changes.record(self._document, value)
        causes.document(self, self._document, value)
        self._document = value
        if hasattr(self, "skin_status"):
            self.skin_status.changed()

    def initialize_scheduler(self) -> None:
        from .tissue_inspection import Inspection

        self.initialize_project_preparation()
        self.tissue_inspection = Inspection()
        self.clear_previews()
        self.scheduler = TaskCoordinator(
            lambda: self.document, executor_factory=self.executor_factory
        )
        self.scheduler.profiler = self.profiler
        self.scheduler.can_publish = self.can_publish
        self.attach_shortcut_contexts()
        if hasattr(self, "issues"):
            self.issues.reset()

    def initialize_project_preparation(self) -> None:
        from .assembly_runtime import Assembly
        from .skeleton_runtime import SkeletonUpdate

        self.assembly = Assembly(self)
        self.skeleton_update = SkeletonUpdate(self)

    def attach_shortcut_contexts(self) -> None:
        from .formula_invalidation import FormulaInvalidation
        from .shortcut_comparison import Comparison
        from .shortcut_contexts import Contexts
        from .shortcut_observation import Observation

        self.shortcut_edits = Contexts(self)
        self.formula_invalidation = FormulaInvalidation()
        self.shortcut_observation = Observation(self)
        self.shortcut_comparison = Comparison(self)
        self.scheduler.observer = self.shortcut_observation.event
        self.scheduler.annotate = self.shortcut_edits.annotate
        self.scheduler.before_dispatch = self.shortcut_edits.require

    def synchronize_services(self) -> None:
        self.issues.synchronize()
        self.shortcut_edits.synchronize()
        self.shortcut_observation.prune()

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
        from .workspace_policy import included

        return 10 if any(included(self.document, self.workspace, key) for key in ids) else 0

    def editable(self, entity_id: str) -> SCP:
        from anthroforge.core.mirroring import require_source

        require_source(entity_id)
        if self.waiting_save:
            raise ValueError("Editing is blocked while waiting to save.")
        if self.workspace.focused and entity_id not in self.workspace.members:
            raise ValueError("This SCP is outside the focused workspace and is read-only.")
        return self.document.entity(entity_id)

    def replace_document(
        self, *, accepted_outputs: frozenset[Port] = frozenset(), **changes: Any
    ) -> None:
        before = self.document
        self.document = self.validated_replacement(changes)
        self.history.observe(self.document)
        self.observe_replacement(before, accepted_outputs)

    def validated_replacement(self, changes: dict[str, Any]) -> Document:
        from .property_guards import require_changes
        from .shortcut_contexts import superseded

        before = self.document
        self.serial += 1
        updated = replace(self.document, revision=self.serial, **retain_settings(before, changes))
        require_mirror_transition(before, updated)
        contexts = superseded(self, before, updated)
        if contexts != updated.shortcut_edits:
            updated = replace(updated, shortcut_edits=contexts)
        require_changes(self, before, updated)
        return updated

    def observe_replacement(
        self, before: Document, accepted_outputs: frozenset[Port] = frozenset()
    ) -> None:
        from . import formula_observation, routing_membership, tissue_stack_observation

        routing_membership.changed(self, before, accepted_outputs)
        tissues = frozenset(p.owner for p in accepted_outputs if p.output == "final")
        formulas = frozenset(p.owner for p in accepted_outputs if p.output == "formula")
        tissue_stack_observation.changed(self, before, tissues)
        formula_observation.changed(self, before, formulas)

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
        self.shortcut_edits.active = ""
        self.comparison_event("begin")

    @measured("transaction", lambda session: session.profiler)
    def commit(self) -> None:
        self.history.commit(self.document, self.replay_callback)
        self.replay_callback = None
        from .operations import released

        released(self)
        self.shortcut_edits.active = ""
        self.shortcut_observation.finish_gesture()
        self.comparison_event("commit")

    @measured("transaction", lambda session: session.profiler)
    def cancel(self) -> None:
        self.comparison_event("cancel")
        self.shortcut_observation.finish_gesture(cancelled=True)
        self.shortcut_edits.active = ""
        self.document = replace(self.history.cancel(), workspaces=self.document.workspaces)
        self.scheduler.restore(self.history.surviving())
        self.replay_callback = None
        self.issues.reset()
        self.resume_calculations()

    @measured("transaction", lambda session: session.profiler)
    def navigate(self, direction: int) -> None:
        if self.waiting_save:
            raise ValueError("History is blocked while waiting to save.")
        previous = self.document
        self.comparison_event("undo" if direction < 0 else "redo")
        self.shortcut_observation.restore()
        self.document = replace(self.history.navigate(direction), workspaces=previous.workspaces)
        self.remember_restarts(self.scheduler.restore(self.history.surviving()))
        changed = changed_ids(previous, self.document)
        self.scheduler.invalidate(changed)
        self.issues.reset()
        if direction > 0:
            self.history.replay()
        self.history.recover()
        self.resume_calculations()

    def remember_restarts(self, restarts: list[Restart]) -> None:
        for restart in restarts:
            for entry in self.history.entries[self.history.cursor + 1 :]:
                if restart.revision in entry.versions:
                    entry.restarts.append(restart.callback)
                    break

    def resume_calculations(self) -> None:
        from . import evaluation, shortcut_contexts
        from .construction_tasks import schedule
        from .control_tasks import resume
        from .geometry_outputs import items
        from .output_tasks import pending

        shortcut_contexts.resume(self)
        resume(self)
        pending(self)
        targets = {e.id for e in self.document.entities if e.status in ("edited", "stale")}
        captures = {e.id for e in self.document.entities if e.status == "edited"}
        if targets and self.document.attachments_enabled and self.document.update_mode != "MANUAL":
            evaluation.request(self, targets, captures)
        schedule(self, {e.id for e in items(self.document) if e.result.status == "pending"})

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
        self.comparison_event("wait")

    def comparison_event(self, operation: str) -> None:
        from .comparison_journal import record

        record(self, operation)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.document.name,
            "id": str(self.document.id),
            "revision": self.document.revision,
            "metres_per_unit": 1.0,
            "entity_count": len(self.document.entities),
            "skin_available": self.skin_status.snapshot().operations["export"].available,
            "entities": [asdict(item) for item in self.document.entities],
            "controls": [asdict(item) for item in self.document.controls],
            "objects": object_descriptions(self.document),
            **activity_description(self),
            "workspace": asdict(self.workspace),
        }

    def close(self) -> None:
        self.assembly.cancel()
        self.skeleton_update.cancel()
        self.shortcut_comparison.clear()
        self.issues.close()
        self.scheduler.close()
        self.clear_previews()
        if self._engine is not None:
            self._engine.clear_caches()
            self.profiler.native.detach(self._engine)
        if self.owns_profiler:
            self.profiler.close()
        if self.file_lock:
            self.file_lock.close()

    def clear_previews(self) -> None:
        self.conversion = ConversionPreview()
        self.mesh_replacement: Preview[Any] = Preview()
        self.tissue_retarget: Preview[Any] = Preview()
        self.surface_preview: Preview[Candidate] = Preview()
        self.tissue_preview: Preview[TissueCandidate] = Preview()
        self.skin_fit_preview: Preview[Any] = Preview()


def changed_ids(previous: Document, current: Document) -> set[str]:
    changed = {e.id for e in previous.entities if e != current.index.entities.get(e.id)}
    changed |= {c.id for c in previous.controls if c != current.index.controls.get(c.id)}
    return changed | {o.id for o in previous.objects if o != current.registry.authored.get(o.id)}


def object_descriptions(document: Document) -> list[dict[str, Any]]:
    from .object_codec import encode

    return [encode(item) for item in document.objects]


def activity_description(session: Session) -> dict[str, Any]:
    return {
        "jobs": [job.describe() for job in session.scheduler.jobs],
        "save_blocked": session.scheduler.blocked,
        "checkpoint_revision": session.scheduler.checkpoint.revision,
    }


def merge_entity(previous: SCP, current: SCP) -> SCP:
    if current is previous:
        return current
    moved = differs(previous, current, POSE_FIELDS)
    return replace(current, pose_revision=previous.pose_revision + 1) if moved else current
