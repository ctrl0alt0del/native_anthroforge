"""Mapping choices are qualified by a real preparation/reference, never client descriptions."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.surface_references import SurfaceReference

from . import assembly_choices, choice_queries, surface_options


def context(session: Any, kind: str, token: str, reference: str, controls: bool = False) -> Any:
    if kind == "assembly" and not token:
        return session.document, session.document, persisted_reference(session, reference)
    runtime, state, row = prepared_reference(session, kind, token, reference, controls)
    if controls:
        return state.candidate.baseline, state.candidate.document, row
    source = runtime.source.source
    return source.document if source else session.document, session.document, row


def prepared_reference(session: Any, kind: str, token: str, reference: str, controls: bool) -> Any:
    service = getattr(session, kind)
    runtime = service if kind == "assembly" else service.runtime
    state, status = runtime.preparation, service.status()
    if not token or token != state.token or state.state != "ready" or state.candidate is None:
        raise ValueError("Choose a reference from the current completed preparation.")
    state.candidate.reads.require(session.document)
    rows = status.get("controls" if controls else "mappings", ())
    row = next((r for r in rows if r["key"] == reference), None)
    if row is None:
        raise ValueError("Unknown mapping reference in this preparation.")
    return runtime, state, row


def persisted_reference(session: Any, reference: str) -> dict[str, Any]:
    value = next((r for r in session.document.external_references if r.id == reference), None)
    if value is None or value.target or not value.uses:
        raise ValueError("Unknown unresolved project reference.")
    return reference_row(value)


def reference_row(value: Any) -> dict[str, Any]:
    return dict(
        key=value.id,
        source=value.id,
        name=value.name,
        kind=value.kind,
        role=value.uses[0].role,
        relationship=value.uses[0].relationship,
        property=dict(asdict(value.property), target=value.id) if value.property else None,
    )


def target_rows(session: Any, kind: str, token: str, reference: str, controls: bool = False) -> Any:
    _, document, row = context(session, kind, token, reference, controls)
    return [qualified(document, row, target) for target in assembly_choices.targets(document, row)]


def qualified(document: Any, reference: Any, target: Any) -> dict[str, Any]:
    role = reference.get("role")
    ref = SurfaceReference(target["target"], role, target["instance"]) if role else None
    surface = surface_options.row(document, ref) if ref else {}
    return dict(
        target,
        compatible=True,
        ready=surface.get("ready", True),
        role=role or "",
        reason=surface.get("reason", ""),
        correspondence="assessed during preparation" if role else "not applicable",
    )


def property_rows(
    session: Any, kind: str, token: str, reference: str, target: str, controls: bool = False
) -> Any:
    source, destination, row = context(session, kind, token, reference, controls)
    if not row.get("property"):
        return []
    return assembly_choices.properties(source, destination, row, target)


def targets(
    session: Any, kind: str, token: str, reference: str, controls: bool = False, **paging: Any
) -> dict[str, Any]:
    rows = target_rows(session, kind, token, reference, controls)
    return choice_queries.project(session, rows, (kind, token, reference, controls), **paging)


def properties(
    session: Any,
    kind: str,
    token: str,
    reference: str,
    target: str,
    controls: bool = False,
    **paging: Any,
) -> dict[str, Any]:
    rows = property_rows(session, kind, token, reference, target, controls)
    return choice_queries.project(
        session, rows, (kind, token, reference, target, controls), **paging
    )
