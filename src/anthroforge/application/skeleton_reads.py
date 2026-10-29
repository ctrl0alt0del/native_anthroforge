"""Candidate read closure includes automatic membership and non-scene numerical controls."""

from typing import Any

from anthroforge.core.jobs import ObsoleteInputs

from . import dependencies, skin_update_tasks, tissue_stack_observation


def keys(context: Any, required: Any, extra: Any) -> set[str]:
    observed = set(required)
    for port in context.prepared:
        if port.output in ("plan", "final"):
            observed |= tissue_stack_observation.ports(context.document, port.owner, port.output)
    if context.document.skin.reference:
        observed |= skin_update_tasks.inputs(context.resources, context.document)
    found = {p.owner for p in observed} & set(context.baseline.registry.records)
    return found | set(extra) | control_keys(context, observed)


def control_keys(context: Any, observed: Any) -> set[str]:
    found: set[str] = set()
    formulas = context.baseline.formula_index.formulas
    for port in observed:
        if port.owner in formulas:
            found.update((formulas[port.owner][0].id, "formula-result:" + port.owner))
    for group in ("shortcuts", "driving_shortcuts"):
        after = {v.id: v for v in getattr(context.document, group)}
        found.update(v.id for v in getattr(context.baseline, group) if after.get(v.id) != v)
    found.update("mirror:" + key for key in context.baseline.mirrors.rules)
    found.add("mirror_relationships")
    found.add("formula_writers")
    return found


def scene(document: Any, scopes: Any = (True, True)) -> tuple[Any, ...]:
    graph = dependencies.graph(document)
    return (
        graph.routing_scene if scopes[0] else None,
        tissue_stack_observation.membership(document) if scopes[1] else None,
    )


def observed_scene(context: Any, required: Any) -> tuple[Any, ...]:
    scope = {p.output for p in required}
    stacking = any(p.output in ("plan", "final") for p in context.prepared)
    return scene(context.baseline, ("routing_scope" in scope, stacking))


def relationships(graph: Any, affected: Any) -> tuple[Any, ...]:
    return tuple(
        (p, graph.get(p, frozenset()), graph.consumers.get(p, frozenset()))
        for p in affected
        if p in graph
    )


def require_global(reads: Any, document: Any) -> None:
    scopes = tuple(value is not None for value in reads.scene)
    if reads.scene != scene(document, scopes):
        raise ObsoleteInputs("Automatic obstacle or stacking membership changed; prepare again.")
    if reads.skin is not None and reads.skin != document.skin:
        raise ObsoleteInputs("Skin state changed while preparing this update; prepare again.")


def merge_order(candidate: Any, current: Any) -> tuple[str, ...]:
    old = candidate.baseline.shortcut_order
    new = candidate.document.shortcut_order
    if old == new:
        return tuple(current.shortcut_order)
    available = {
        v.id for v in (*candidate.document.shortcuts, *candidate.document.driving_shortcuts)
    }
    retained = (key for key in current.shortcut_order if key not in old and key in available)
    return tuple(dict.fromkeys((*new, *retained)))
