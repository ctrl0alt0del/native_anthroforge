"""Resolve shared authored curves into owned consumer-local evaluation inputs."""

from dataclasses import fields, replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Curve, Primitive, ResolvedPrimitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.results import Port
from anthroforge.native.construction import matrix
from anthroforge.native.mesh import GeometryEngine

from . import object_revisions
from .object_frames import Frames

if TYPE_CHECKING:
    from .session import Session


def source(document: Document, key: str) -> Curve:
    item = document.object(key)
    if not isinstance(item, Curve):
        raise ValueError("Construction source must be a curve or fiber.")
    return item


def world(engine: GeometryEngine, document: Document, key: str) -> tuple[float, ...]:
    return Frames(engine, document).world(key)


def parameters(value: Primitive | ResolvedPrimitive) -> dict[str, Any]:
    return {f.name: getattr(value, f.name) for f in fields(value) if f.name != "curves"}


def use_frame(engine: GeometryEngine, document: Document, use: CurveUse) -> tuple[float, ...]:
    if use.mode == "SHAPE_ONLY":
        return use.matrix
    frame = world(engine, document, use.reference_frame)
    current = matrix(engine, frame, world(engine, document, use.curve), relative=True)
    delta = matrix(engine, use.bind_matrix, current, relative=True)
    return matrix(engine, use.matrix, delta)


def resolve_curve(engine: GeometryEngine, document: Document, use: CurveUse) -> Curve:
    curve = source(document, use.curve)
    return replace(curve, matrix=use_frame(engine, document, use), start=use.start, span=use.span)


def resolve(engine: GeometryEngine, document: Document, entity: SCP) -> ResolvedPrimitive:
    definition = entity.primitive
    if definition is None:
        raise ValueError("This SCP has no construction.")
    if isinstance(definition, ResolvedPrimitive):
        return definition
    curves = tuple(resolve_curve(engine, document, use) for use in definition.curves)
    return ResolvedPrimitive(**parameters(definition), curves=curves)


def for_editing(session: "Session", entity: SCP | None) -> SCP | None:
    if entity is None or entity.primitive is None:
        return entity
    return replace(entity, primitive=editing_definition(session, entity))


def editing_definition(session: "Session", entity: SCP) -> ResolvedPrimitive:
    from .curve_edit_state import current

    definition = resolve(session.engine, session.document, entity)
    curves = tuple(
        replace(curve, points=current(session, curve).points) for curve in definition.curves
    )
    return replace(definition, curves=curves)


def owned_use(curve: Curve, owner: str) -> CurveUse:
    return CurveUse(
        curve.id,
        start=curve.start,
        span=curve.span,
        matrix=curve.matrix,
        bind_matrix=curve.matrix,
        reference_frame=owner,
    )


def create_records(
    definition: ResolvedPrimitive, owner: str
) -> tuple[Primitive, tuple[Curve, ...]]:
    curves = tuple(
        replace(c, parent=owner, owners=(owner,), start=None, span=None) for c in definition.curves
    )
    uses = tuple(owned_use(c, owner) for c in definition.curves)
    return Primitive(**parameters(definition), curves=uses), curves


def consumers(document: Document, curves: set[str]) -> set[str]:
    return set().union(*(document.registry.consumers.get(key, ()) for key in curves))


def edited_source(session: "Session", use: CurveUse, curve: Curve) -> Curve:
    from .curve_edit_state import prepare

    original = source(session.document, use.curve)
    changes = {
        f.name: getattr(curve, f.name)
        for f in fields(curve)
        if f.name not in ("matrix", "start", "span")
    }
    changed = replace(original, **changes)
    if curve.matrix != use_frame(session.engine, session.document, use):
        changed = replace(changed, matrix=authored_matrix(session, use, curve.matrix))
    return object_revisions.authored(original, prepare(session, original, changed))


def authored_matrix(
    session: "Session", use: CurveUse, edited: tuple[float, ...]
) -> tuple[float, ...]:
    curve = source(session.document, use.curve)
    delta = matrix(session.engine, use.matrix, edited, relative=True)
    relative = matrix(session.engine, use.bind_matrix, delta)
    absolute = matrix(
        session.engine, world(session.engine, session.document, use.reference_frame), relative
    )
    return matrix(
        session.engine,
        world(session.engine, session.document, curve.parent),
        absolute,
        relative=True,
    )


def install(session: "Session", entity: SCP, definition: ResolvedPrimitive) -> set[str]:
    from .junction_edits import expand

    assert isinstance(entity.primitive, Primitive)
    previous = {use.id: use for use in entity.primitive.curves}
    curves = expand(session, edited_curves(session, entity.id, previous, definition))
    uses = tuple(updated_use(previous, c, entity.id) for c in definition.curves)
    changed = {
        key for key, value in curves.items() if value != session.document.registry.records.get(key)
    }
    primitive = Primitive(**parameters(definition), curves=uses)
    publish_authored(session, entity, primitive, curves)
    return consumers(session.document, changed) | {entity.id}


def edited_curves(
    session: "Session", owner: str, previous: dict[str, CurveUse], definition: ResolvedPrimitive
) -> dict[str, Curve]:
    return {
        c.id: edited_source(session, previous[c.id], c)
        if c.id in previous
        else replace(c, parent=owner, owners=(owner,), start=None, span=None)
        for c in definition.curves
    }


def updated_use(previous: dict[str, CurveUse], curve: Curve, owner: str) -> CurveUse:
    if curve.id in previous:
        return replace(previous[curve.id], start=curve.start, span=curve.span)
    return owned_use(curve, owner)


def publish_authored(
    session: "Session", entity: SCP, primitive: Primitive, curves: dict[str, Curve]
) -> None:
    from .entity_revisions import authored
    from .path_tasks import edited

    existing = session.document.registry.construction
    objects = tuple(curves.get(o.id, o) for o in session.document.objects)
    objects += tuple(c for key, c in curves.items() if key not in existing)
    changed = authored(entity, replace(entity, primitive=primitive))
    entities = tuple(changed if e.id == entity.id else e for e in session.document.entities)
    updates = {key for key, value in curves.items() if value != existing.get(key)}
    invalidate(session, entity.id, updates)
    session.replace_document(entities=entities, objects=objects)
    edited(session, {Port(key, "path") for key in updates})


def invalidate(session: "Session", entity: str, curves: set[str]) -> None:
    from anthroforge.core.results import Port

    session.scheduler.invalidate_ports(
        {Port(entity, "geometry")} | {Port(c, "path") for c in curves}
    )
