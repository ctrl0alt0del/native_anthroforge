"""Edit-context ownership across gestures, pending calculations, history and saves."""

from typing import Any

from anthroforge.core.entities import descendants
from anthroforge.core.jobs import ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.shortcut_edits import ShortcutEdit
from anthroforge.core.shortcuts import AttachmentPolicy

from . import dependencies, shortcut_capture, shortcut_ownership


class Contexts:
    def __init__(self, session: Any) -> None:
        self.session, self.active = session, ""

    def current(self) -> tuple[str, ...]:
        scheduler = self.session.scheduler
        if scheduler.publishing:
            return tuple(scheduler.publication_contexts)
        return (self.active,) if self.active else ()

    def begin(self, shortcut: Any) -> None:
        from .shortcut_operations import validate_policy

        validate_policy(self.session.document, shortcut)
        self.session.shortcut_observation.begin(shortcut)
        existing = lookup(self.session.document, self.active)
        if existing is not None and existing.shortcut == shortcut.id:
            return
        bindings = shortcut_capture.retained_bindings(self.session.document, shortcut)
        if bindings or shortcut.policy != AttachmentPolicy():
            self.activate(definition(self.session.document, shortcut, bindings))

    def activate(self, context: ShortcutEdit) -> None:
        self.active = context.id
        retained = tuple(
            v
            for v in self.session.document.shortcut_edits
            if not set(v.targets) & set(context.targets)
        )
        self.session.replace_document(shortcut_edits=(*retained, context))
        from .shortcut_capture_tasks import request

        if context.status == "pending":
            request(self.session, context.id)

    def annotate(self, job: Any, document: Any) -> None:
        if not job.writes or not job.publish_during_edit or not document.shortcut_edits:
            return
        origins = {v.id for v in document.shortcut_edits if set(v.targets) & job.outputs}
        if job.kind == "shortcut_capture":
            origins |= set(job.edit_contexts)
        job.edit_contexts = tuple(sorted(origins))
        if job.kind != "shortcut_capture":
            job.prerequisites |= frozenset(Port(key, "shortcut_capture") for key in origins)

    def require(self, job: Any, document: Any) -> None:
        if job.kind == "shortcut_capture":
            return
        for key in job.edit_contexts:
            context = lookup(document, key)
            if context is None:
                raise ObsoleteInputs("The initiating shortcut edit was superseded.")
            if context.status != "ready":
                raise ValueError(context.error or "Shortcut attachment preparation is unavailable.")

    def synchronize(self) -> None:
        session = self.session
        if session.history.before is not None or not session.document.shortcut_edits:
            return
        running = {key for job in session.scheduler.active_jobs for key in job.edit_contexts}
        retained = tuple(
            v
            for v in session.document.shortcut_edits
            if v.id in running or v.status != "ready" or waiting(session.document, v)
        )
        if retained != session.document.shortcut_edits:
            session.replace_document(shortcut_edits=retained)


def lookup(document: Any, key: str) -> ShortcutEdit | None:
    return next((v for v in document.shortcut_edits if v.id == key), None)


def definition(document: Any, shortcut: Any, bindings: tuple[Any, ...] = ()) -> ShortcutEdit:
    owner = shortcut_ownership.attachment_scope(document, shortcut)
    capture = shortcut.policy.backsolve or bool(shortcut.policy.descendants)
    return ShortcutEdit(
        shortcut.id,
        owner,
        shortcut.policy,
        affected_targets(document, shortcut, owner),
        shortcut_capture.source_entities(document, owner, shortcut.policy) if capture else (),
        bindings=bindings,
        status="pending" if capture else "ready",
    )


def affected_targets(document: Any, shortcut: Any, owner: str) -> tuple[str, ...]:
    controlled = shortcut_ownership.targets(document, shortcut)
    graph = dependencies.graph(document)
    seeds = {p for p in graph if p.owner in controlled}
    affected = {p.owner for p in dependencies.closure(graph.consumers, seeds)}
    affected |= descendants(document.entities, owner)
    return tuple(sorted(affected | controlled))


def waiting(document: Any, context: ShortcutEdit) -> bool:
    for key in context.targets:
        item = document.registry.records.get(key)
        if item is not None and item.result.status in ("pending", "failed"):
            return True
        if getattr(item, "parent", "") and getattr(item, "status", "ready") in (
            "edited",
            "stale",
            "failed",
        ):
            return True
    return any(
        r.formula in context.targets and r.status in ("pending", "failed")
        for r in document.formula_results
    )


def superseded(session: Any, before: Any, after: Any) -> tuple[ShortcutEdit, ...]:
    if session.shortcut_edits.current() or not before.shortcut_edits:
        return tuple(after.shortcut_edits)
    records = before.registry.records
    changed = {
        key
        for key, item in after.registry.records.items()
        if key in records and item.generation != records[key].generation
    }
    removed = {c.id for c in before.shortcut_edits if set(c.targets) & changed}
    return tuple(c for c in after.shortcut_edits if c.id not in removed)


def install(session: Any, context: ShortcutEdit) -> None:
    if lookup(session.document, context.id) is None:
        raise ObsoleteInputs("The initiating shortcut edit was superseded.")
    session.replace_document(
        shortcut_edits=tuple(
            context if v.id == context.id else v for v in session.document.shortcut_edits
        )
    )


def resume(session: Any) -> None:
    from .shortcut_capture_tasks import request

    running = {
        port.owner
        for job in session.scheduler.active_jobs
        for port in job.provides
        if port.output == "shortcut_capture"
    }
    for context in session.document.shortcut_edits:
        if context.status == "pending" and context.id not in running:
            request(session, context.id)
