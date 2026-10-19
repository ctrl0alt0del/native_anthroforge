"""Composition of evaluated construction families under the existing task coordinator."""

from typing import Any

from anthroforge.core.results import Port

from . import anchor_tasks, construction_tasks, dependencies, geometry_outputs, path_tasks

FAMILIES = (("path", path_tasks), ("binding", anchor_tasks))


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
    outputs = dependencies.closure(dependencies.reverse(graph), seeds) - seeds
    waiting = set().union(*(j.provides for j in session.scheduler.active_jobs if j.future is None))
    outputs -= waiting
    for role, family in FAMILIES:
        family.schedule(session, {p.owner for p in outputs if p.output == role})
    targets = {p.owner for p in outputs if p.output == "geometry"}
    geometry_outputs.pending(session, targets)
    construction_tasks.schedule(session, targets)
