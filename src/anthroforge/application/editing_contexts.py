"""Owned editable scenes, explicit callback scopes and coherent project projections."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from threading import get_ident
from typing import Any, cast

from anthroforge.core.document import Document
from anthroforge.core.reconstruction import Reconstruction, SceneSnapshot

from .changes import ChangeJournal
from .editing_state import EditingState
from .history import History
from .scheduling_context import SchedulingContext


class EditingContexts:
    def __init__(self, session: Any) -> None:
        self.session, self.thread = session, get_ident()
        self.states = {"": session._editing}
        self.visible = ""
        session.scheduler.context_scope = self.use

    @contextmanager
    def use(self, key: str) -> Iterator[None]:
        if get_ident() != self.thread:
            raise RuntimeError("Editing context access belongs to the application thread.")
        session = self.session
        before = session._editing
        session._editing = self.states[key]
        session.scheduler.context = key
        try:
            yield
        finally:
            session._editing = before
            session.scheduler.context = before.key

    def add(self, key: str, document: Document) -> None:
        if key in self.states:
            raise ValueError("Editing context already exists.")
        self.states[key] = EditingState(key, initial_values(document))
        self.session.scheduler.scheduling_contexts[key] = SchedulingContext(document)
        with self.use(key):
            initialize_services(self.session)

    def select(self, key: str) -> None:
        if self.session.history.before is not None or self.session.waiting_save:
            raise ValueError("Finish the current gesture or save before switching variants.")
        if key not in self.states:
            raise ValueError("Unknown editing context.")
        self.flush()
        self.pause(self.visible)
        self.visible = key
        self.session._editing = self.states[key]
        self.session.scheduler.context = key
        self.session.serial = max(self.session.serial, self.session.document.revision)

    def pause(self, key: str) -> None:
        with self.use(key):
            self.session.cancel_painting()
            for job in self.session.scheduler.active_jobs:
                if job.writes:
                    self.session.scheduler.cancel_job(job.id, obsolete=True, reason="context_left")

    def scene(self, key: str, committed: bool = False) -> Document:
        state = self.states[key].values
        before = state["history"].before
        return cast(Document, before if committed and before is not None else state["document"])

    def project(self, committed: bool = False) -> Document:
        accepted = self.scene("", committed)
        state = accepted.reconstruction
        snapshots = {row.id: row for row in state.snapshots}
        for variant in state.variants:
            if variant.id in self.states:
                scene = bare(self.scene(variant.id, committed))
                snapshots[variant.current] = SceneSnapshot(scene, variant.current)
        state = replace(state, snapshots=tuple(snapshots.values()))
        return replace(accepted, reconstruction=state, revision=self.session.serial)

    def flush(self) -> None:
        projected = self.project(committed=True)
        state = self.states[""].values
        state["document"] = projected
        state["history"].observe(projected)

    def documents(self) -> list[Document]:
        result = []
        for state in self.states.values():
            result.append(state.values["document"])
            result.extend(entry.document for entry in state.values["history"].entries)
            if state.values["history"].before is not None:
                result.append(state.values["history"].before)
        return result

    def close(self) -> None:
        for key in tuple(self.states):
            self.close_context(key)

    def close_context(self, key: str) -> None:
        with self.use(key):
            self.session.assembly.cancel()
            self.session.skeleton_update.cancel()
            self.session.variant_review.cancel()
            self.session.reconstruction_comparison.cancel()
            self.session.shortcut_comparison.clear()
            self.session.issues.close()
            self.session.clear_previews()

    def prune(self) -> None:
        retained = {v.id for v in self.scene("").reconstruction.variants}
        for key in tuple(self.states):
            if key in retained or key == self.visible or not self.scene(key).editing_scope:
                continue
            self.pause(key)
            self.close_context(key)
            if self.session.scheduler.scheduling_contexts[key].registry.active:
                continue
            del self.states[key]
            del self.session.scheduler.scheduling_contexts[key]

    def adopt_published(self, document: Document, resources: Any) -> None:
        if any(
            key and state.registry.active
            for key, state in self.session.scheduler.scheduling_contexts.items()
        ):
            raise ValueError("Finish context jobs before adopting another project.")
        self.close()
        session = self.session
        session._editing = self.states[""]
        session._editing.values = initial_values(document)
        session._document, session.resources = document, resources
        session.scheduler.context = ""
        session.scheduler.scheduling_contexts = {"": session.scheduler.scheduling_contexts[""]}
        initialize_services(session)
        session.contexts = EditingContexts(session)


def bare(document: Document) -> Document:
    return (
        replace(document, reconstruction=Reconstruction())
        if document.reconstruction != Reconstruction()
        else document
    )


def initial_values(document: Document) -> dict[str, Any]:
    return dict(
        document=document,
        history=History(document),
        changes=ChangeJournal(),
        formula_write_authority=frozenset(),
        formula_observing=False,
        active_workspace=0,
        replay_callback=None,
    )


def initialize_services(session: Any) -> None:
    from .issues.repairs import register
    from .issues.system import IssueSystem
    from .skin_status import SkinStatusProvider
    from .tissue_inspection import Inspection

    session.initialize_project_preparation()
    session.clear_previews()
    session.tissue_inspection = Inspection()
    session.attach_shortcut_contexts()
    session.issues = IssueSystem(session)
    session.skin_status = SkinStatusProvider(session)
    register(session)
