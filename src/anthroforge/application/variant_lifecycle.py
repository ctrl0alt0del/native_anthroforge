"""Alternative lifetime and support freshness, separate from geometry evaluation."""

from dataclasses import asdict, replace
from typing import Any

from . import dependencies, variant_operations
from .assembly_candidate import read_record


def describe(session: Any, state: Any, record: Any) -> dict[str, Any]:
    changes = (
        support_changes(session, state.snapshot(record.current)) if not record.checkpoint else []
    )
    return dict(asdict(record), outdated=bool(changes), changed_supports=changes)


def support_changes(session: Any, document: Any) -> list[str]:
    if document.editing_scope is None:
        return []
    scope = document.editing_scope
    graph = dependencies.graph(document)
    seeds = {port for port in graph if port.owner in scope.editable}
    inputs = dependencies.closure(graph, seeds)
    keys = {port.owner for port in inputs} & scope.pinned
    accepted = session.contexts.scene("")
    return sorted(k for k in keys if read_record(document, k) != read_record(accepted, k))


def remove(session: Any, variant: str) -> None:
    variant_operations.require_idle(session)
    state = variant_operations.state(session)
    state.variant(variant)
    require_unreferenced(state, variant)
    if session.contexts.visible == variant:
        variant_operations.select(session)
    rows = tuple(v for v in state.variants if v.id != variant)
    retained = {s for v in rows for s in (v.baseline, v.current)}
    snapshots = tuple(s for s in state.snapshots if s.id in retained)
    variant_operations.install(session, replace(state, variants=rows, snapshots=snapshots))
    session.contexts.prune()


def require_unreferenced(state: Any, key: str) -> None:
    if any(v.parent == key for v in state.variants):
        raise ValueError("Remove dependent variants/checkpoints before removing this source.")
    if any(w.variant == key or w.checkpoint == key for w in state.work):
        raise ValueError("This variant is referenced by reconstruction work.")
    if any(r.variant == key for r in (*state.regions, *state.stages, *state.reviews)):
        raise ValueError("This variant retains regions, reference stages or review history.")
