"""Shared point edits expand once into an atomic authored-object update."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.entities import IDENTITY
from anthroforge.core.junctions import PointRef, members
from anthroforge.native import construction, curve_editing

from . import curve_edit_state, curve_sources, junction_bindings, object_revisions


def point(item: Curve, identity: str) -> Any:
    value = next((p for p in item.points if p.id == identity), None)
    if value is None:
        raise ValueError("Unknown authored junction point.")
    return value


def world_position(session: Any, item: Curve, identity: str) -> Any:
    frame = curve_sources.world(session.engine, session.document, item.id)
    return session.engine.world_point(frame, point(item, identity).position)


def positioned(session: Any, item: Curve, ref: PointRef, world: Any, junction: str) -> Curve:
    if item.engine == "PARAMETRIC":
        return parametric_membership(session, item, ref, world, junction)
    frame = curve_sources.world(session.engine, session.document, item.id)
    inverse = construction.matrix(session.engine, frame, IDENTITY, relative=True)
    position = session.engine.world_point(inverse, world)
    index = next(i for i, p in enumerate(item.points) if p.id == ref.point)
    changed = curve_editing.point(session.engine, item, index, dict(position=position))
    points = tuple(
        replace(changed, junction=junction) if p.id == ref.point else p for p in item.points
    )
    return replace(item, points=points)


def parametric_membership(
    session: Any, item: Curve, ref: PointRef, world: Any, junction: str
) -> Curve:
    from .parametric_junctions import require_position

    require_position(session, item, point(item, ref.point), world)
    return replace(
        item,
        points=tuple(
            replace(p, junction=junction) if p.id == ref.point else p for p in item.points
        ),
    )


def expand(session: Any, changes: dict[str, Any]) -> dict[str, Any]:
    if not session.document.junctions:
        return changes
    links = members(session.document.objects)
    result = dict(changes)
    for key, item in changes.items():
        before = session.document.registry.records.get(key)
        if isinstance(before, Curve) and isinstance(item, Curve):
            expand_curve(session, before, item, result, links)
    junction_bindings.expand(session, changes, result)
    return prepared(session, result)


def prepared(session: Any, result: Any) -> dict[str, Any]:
    return {
        key: revised(session, session.document.object(key), item)
        if key in session.document.registry.records
        else item
        for key, item in result.items()
    }


def revised(session: Any, before: Any, after: Any) -> Any:
    return object_revisions.authored(before, curve_edit_state.prepare(session, before, after))


def expand_curve(session: Any, before: Curve, after: Curve, result: Any, links: Any) -> None:
    if before.points == after.points:
        return
    opening = curve_edit_state.current(session, before)
    previous = {p.id: p for p in opening.points}
    if any(p.junction and p.id not in {v.id for v in after.points} for p in opening.points):
        raise ValueError("Detach a shared junction point before removing it.")
    for value in after.points:
        old = previous.get(value.id)
        if not old or not value.junction or old.position == value.position:
            continue
        world = world_position(session, after, value.id)
        expand_members(session, result, links[value.junction], world, value.junction, after.id)


def expand_members(
    session: Any, changes: Any, refs: Any, world: Any, junction: str, skip: str = ""
) -> None:
    from .symmetric_junctions import project

    constrained = project(session, refs, world)
    if constrained is not world:
        skip, world = "", constrained
    for ref in refs:
        if ref.curve == skip:
            continue
        item = changes.get(ref.curve) or curve_edit_state.current(
            session, curve_sources.source(session.document, ref.curve)
        )
        changes[ref.curve] = positioned(session, item, ref, world, junction)
