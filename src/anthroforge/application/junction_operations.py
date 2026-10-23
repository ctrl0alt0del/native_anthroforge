"""Explicit shared-point lifecycle; no distance-based joining or anatomical wrapper."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.junctions import Junction, PointRef, members
from anthroforge.core.results import Port

from . import (
    curve_edit_state,
    dependent_tasks,
    junction_bindings,
    junction_edits,
    object_operations,
    object_revisions,
)


def member(session: Any, value: dict[str, str]) -> tuple[Curve, PointRef]:
    ref = PointRef(**value)
    item = object_operations.editable(session, ref.curve)
    if not isinstance(item, Curve):
        raise ValueError("Junctions require authored curve or fiber points.")
    item = curve_edit_state.current(session, item)
    junction_edits.point(item, ref.point)
    return item, ref


def create(session: Any, source: dict[str, str], targets: list[dict[str, str]]) -> str:
    from .parametric_junctions import source as select_source

    item, ref = member(session, source)
    references = [ref, *(member(session, value)[1] for value in targets)]
    require_members(session, references)
    ref = select_source(session, references)
    item = session.document.object(ref.curve)
    junction = Junction(ref)
    changes: dict[str, Any] = {}
    world = junction_edits.world_position(session, item, ref.point)
    junction_edits.expand_members(session, changes, references, world, junction.id)
    junction_bindings.joining(session, changes, references, ref)
    install(session, changes, (*session.document.junctions, junction))
    return junction.id


def require_members(session: Any, references: list[PointRef]) -> None:
    if len(references) < 2 or len({p.curve for p in references}) != len(references):
        raise ValueError("Choose at least two points from distinct curves.")
    if any(
        junction_edits.point(session.document.object(r.curve), r.point).junction for r in references
    ):
        raise ValueError("Detach existing junction memberships before joining these points.")


def install(session: Any, changes: dict[str, Any], junctions: tuple[Junction, ...]) -> None:
    changed = {
        key: junction_edits.revised(session, session.document.object(key), item)
        for key, item in changes.items()
    }
    objects = tuple(changed.get(o.id, o) for o in session.document.objects)
    replace(session.document, objects=objects, junctions=junctions)  # Validate before invalidation.
    ports = changed_ports(session, changed)
    session.scheduler.invalidate_ports(ports)
    session.replace_document(objects=objects, junctions=junctions)
    dependent_tasks.changed(session, ports, published=False)


def changed_ports(session: Any, changes: dict[str, Any]) -> set[Port]:
    return set().union(
        *(
            object_revisions.changed_ports(session.document.object(key), item)
            for key, item in changes.items()
        )
    )


def remove(session: Any, junction: str) -> None:
    refs = members(session.document.objects).get(junction)
    if refs is None:
        raise ValueError("Unknown junction.")
    changes = {}
    for ref in refs:
        item, _ = member(session, asdict(ref))
        points = tuple(replace(p, junction="") if p.id == ref.point else p for p in item.points)
        changes[item.id] = replace(item, points=points)
    install(session, changes, tuple(j for j in session.document.junctions if j.id != junction))


def inspect(session: Any, junction: str) -> dict[str, Any]:
    value = next((j for j in session.document.junctions if j.id == junction), None)
    if value is None:
        raise ValueError("Unknown junction.")
    refs = members(session.document.objects)[junction]
    return dict(id=junction, source=asdict(value.source), members=[asdict(r) for r in refs])


def edit(session: Any, item: Any) -> bool:
    if not session.document.junctions or not isinstance(item, Curve):
        return False
    changes = junction_edits.expand(session, {item.id: item})
    if len(changes) == 1:
        return False
    install(session, changes, session.document.junctions)
    return True
