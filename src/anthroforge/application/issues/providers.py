"""Current SCP/control checks; no geometry computation or automatic repairs."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from threading import Event
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.results import Port, geometry_asset

from ..changes import DocumentChanges


@dataclass(frozen=True)
class Provider:
    name: str
    scopes: Callable[[Document], set[str]]
    affected: Callable[[Document, DocumentChanges], set[str]]
    source: Callable[[Document, str], Any]
    check: Callable[[Document, str, Event], tuple[Issue, ...]]


def item(document: Document, scope: str) -> Any:
    return document.index.entities.get(scope) or document.index.controls.get(scope)


def entity_source(document: Document, scope: str) -> Any:
    value = item(document, scope)
    if value is None:
        return None
    result = value.result
    return (
        (value.generation, support_source(document, value)),
        result.revision,
        result.status,
        result.error,
        getattr(value, "status", ""),
        getattr(value, "error", ""),
        getattr(value, "pose_revision", 0),
        getattr(result, "pending", ()),
    )


def entity_scopes(document: Document) -> set[str]:
    return {"document", *document.index.entities, *document.index.controls}


def entity_changes(document: Document, changes: DocumentChanges) -> set[str]:
    relevant = {"@membership", "generation", "result", "status", "error", "pose_revision"}
    rows = {**changes.entities, **changes.controls}
    selected = {key for key, fields in rows.items() if fields & relevant}
    graph = document.index.structure.dependencies
    selected.update(
        p.owner for key in tuple(selected) for p in graph.consumers.get(Port(key, "geometry"), ())
    )
    return entity_scopes(document) if "attachments_enabled" in changes.document else selected


def support_source(document: Document, value: Any) -> Any:
    support = getattr(value, "support", "") or getattr(value, "parent", "")
    parent = document.index.entities.get(support)
    return (
        document.attachments_enabled,
        support,
        geometry_asset(parent),
        parent.result.revision if parent else 0,
    )


def finding(document: Document, scope: str, code: str, summary: str, **values: Any) -> Issue:
    kind = "SCP" if scope in document.index.entities else "CONTROL"
    return Issue(
        "evaluation.v1",
        scope,
        code,
        summary,
        target=scope,
        kind=kind,
        source=fingerprint(entity_source(document, scope)),
        **values,
    )


def evaluation(document: Document, scope: str, cancel: Event) -> tuple[Issue, ...]:
    value = item(document, scope)
    if value is None or cancel.is_set():
        return ()
    rows = list(evaluation_state(document, scope, value))
    rows.extend(pending_support(document, scope, value))
    rows.extend(missing_surface(document, scope, value))
    return tuple(rows)


def evaluation_state(document: Document, scope: str, value: Any) -> tuple[Issue, ...]:
    status = evaluation_status(value)
    if status is None:
        return ()
    code, summary, severity, details = status
    return (
        finding(
            document, scope, code, summary, stage="evaluation", severity=severity, details=details
        ),
    )


PENDING_STATUS = (
    "OUTPUT_PENDING",
    "Output needs recalculation",
    "info",
    "Last accepted output is retained.",
)


def evaluation_status(value: Any) -> tuple[str, str, str, str] | None:
    result = value.result
    if result.status == "failed" or getattr(value, "status", "") == "failed":
        return (
            "EVALUATION_FAILED",
            "Calculation failed",
            "error",
            result.error or getattr(value, "error", ""),
        )
    if result.status == "pending" or getattr(value, "status", "") in ("edited", "stale"):
        return PENDING_STATUS
    return None


def pending_support(document: Document, scope: str, value: Any) -> tuple[Issue, ...]:
    pending = getattr(value.result, "pending", ())
    if not pending:
        return ()
    issue = finding(
        document,
        scope,
        "UPSTREAM_PENDING",
        "Using accepted upstream output",
        stage="dependencies",
        severity="info",
        related=pending,
        evidence=evidence(pending=list(pending)),
    )
    return (issue,)


def missing_surface(document: Document, scope: str, value: Any) -> tuple[Issue, ...]:
    support = getattr(value, "support", "") or getattr(value, "parent", "")
    if not support or value.attachment.parent_mode != "SURFACE_NEAREST":
        return ()
    if scope in document.index.entities and not document.attachments_enabled:
        return ()
    parent = document.index.entities.get(support)
    if parent is None or geometry_asset(parent):
        return ()
    return (surface_issue(document, scope, support),)


def surface_issue(document: Document, scope: str, support: str) -> Issue:
    return finding(
        document,
        scope,
        "ATTACHMENT_SURFACE_MISSING",
        "Attachment has no accepted surface",
        stage="attachment",
        severity="error",
        related=(support,),
        details="Evaluate the support or explicitly choose an object-origin attachment.",
    )


def graph_changes(document: Document, changes: DocumentChanges) -> set[str]:
    fields = {"@membership", "parent", "support", "follow", "deformers", "attachment"}
    rows = (*changes.entities.values(), *changes.controls.values())
    return (
        {"document"}
        if "attachments_enabled" in changes.document or any(fields & v for v in rows)
        else set()
    )


def graph_check(document: Document, scope: str, cancel: Event) -> tuple[Issue, ...]:
    graph = document.index.structure.dependencies
    rows = []
    for port in sorted(graph.blocked, key=lambda p: (p.owner, p.output)):
        if cancel.is_set():
            break
        rows.append(blocked_issue(document, port))
    return tuple(rows)


BLOCKED = Issue(
    "dependencies.v1",
    "document",
    "DEPENDENCY_BLOCKED",
    "Dependency cycle blocks this output",
    severity="error",
    details="This output belongs to a cycle or depends on one. Accepted output is retained.",
)


def blocked_issue(document: Document, port: Port) -> Issue:
    inputs = sorted((p.owner, p.output) for p in document.index.structure.dependencies[port])
    return replace(
        BLOCKED,
        target=port.owner,
        kind="SCP" if port.owner in document.index.entities else "CONTROL",
        stage=port.output,
        source=fingerprint(inputs),
        related=tuple(sorted({owner for owner, _ in inputs})),
        local_key=port.owner,
        evidence=evidence(inputs=inputs),
    )


def builtins() -> tuple[Provider, ...]:
    return (
        Provider("evaluation.v1", entity_scopes, entity_changes, entity_source, evaluation),
        Provider(
            "dependencies.v1",
            lambda _: {"document"},
            graph_changes,
            lambda d, _: d.index.structure.dependencies,
            graph_check,
        ),
    )
