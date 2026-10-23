"""Composition of evaluated construction families under the existing task coordinator."""

from typing import Any

from anthroforge.core.results import Port

from . import (
    anchor_tasks,
    construction_tasks,
    dependencies,
    formula_tasks,
    geometry_outputs,
    path_tasks,
    tissue_tasks,
)

FAMILIES = (
    ({"formula"}, formula_tasks),
    ({"path"}, path_tasks),
    ({"binding"}, anchor_tasks),
    ({"base", "rest", "intrinsic", "plan", "final"}, tissue_tasks),
)


def pending(session: Any, released: bool = False) -> None:
    for _, family in FAMILIES:
        family.pending(session, released=released)


def edited(session: Any, seeds: set[Port]) -> None:
    for _, family in FAMILIES:
        family.edited(session, seeds)


def schedule(session: Any, targets: set[str], explicit: bool = False) -> None:
    for _, family in FAMILIES:
        family.schedule(session, targets, explicit=explicit)


def propagate(session: Any, seeds: set[Port]) -> None:
    graph = dependencies.graph(session.document)
    outputs = dependencies.frontier(dependencies.reverse(graph), seeds, producers(session.document))
    waiting = set().union(*(j.provides for j in session.scheduler.active_jobs if j.future is None))
    outputs -= waiting
    for role, family in FAMILIES:
        family.schedule(session, {p.owner for p in outputs if p.output in role})
    targets = {p.owner for p in outputs if p.output == "geometry"}
    geometry_outputs.pending(session, targets)
    construction_tasks.schedule(session, targets)


def producers(document: Any) -> set[Port]:
    roles = set().union(*(role for role, _ in FAMILIES))
    result = {port for port in dependencies.graph(document) if port.output in roles}
    return result | {Port(item.id, "geometry") for item in geometry_outputs.items(document)}
