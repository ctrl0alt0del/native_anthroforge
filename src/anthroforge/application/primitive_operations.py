"""Primitive and curve authoring operations with shared topology policy."""

from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import BodyPiece, Curve, CurvePoint, Primitive, Thickness
from anthroforge.core.entities import SCP, Attachment
from anthroforge.core.results import EvaluationResult
from anthroforge.native import curve_editing

from . import construction_codec as codec
from . import construction_tasks as tasks
from .construction_policy import require_topology_edit
from .operations import parent_for, require_name
from .presentation import include_created

if TYPE_CHECKING:
    from .session import Session


def straight_curve(y: float = 0.0) -> Curve:
    return Curve((CurvePoint(position=(-0.5, y, 0.0)), CurvePoint(position=(0.5, y, 0.0))))


def default_primitive(kind: str, shape: str) -> Primitive:
    if kind == "LOFT":
        return Primitive(kind, curves=(straight_curve(-0.15), straight_curve(0.15)))
    if kind == "BODY":
        curve = straight_curve()
        return Primitive(kind, curves=(curve,), pieces=(BodyPiece(curve.id, shape),))
    raise ValueError("Create LOFT or BODY; use import for an imported primitive.")


def create(
    session: "Session",
    kind: str,
    parent: str = "",
    name: str = "Primitive",
    shape: str = "CAPSULE",
    definition: dict[str, Any] | None = None,
) -> str:
    primitive = codec.primitive(definition) if definition else default_primitive(kind, shape)
    entity = new_entity(require_name(name), parent_for(session, parent), primitive)
    session.replace_document(entities=(*session.document.entities, entity))
    include_created(session, {entity.id})
    tasks.request(session, entity.id)
    return entity.id


def new_entity(name: str, parent: str, primitive: Primitive | None) -> SCP:
    origin = Attachment(parent_mode="OBJECT_ORIGIN", child_mode="OBJECT_ORIGIN")
    return SCP(
        name,
        parent=parent,
        primitive=primitive,
        attachment=origin,
        result=EvaluationResult(status="pending"),
    )


def definition(session: "Session", entity: str) -> Primitive:
    primitive = session.editable(entity).primitive
    if primitive is None:
        raise ValueError("This SCP has no editable construction.")
    return primitive


def install(session: "Session", entity: str, primitive: Primitive) -> None:
    item = session.editable(entity)
    if item.primitive and item.primitive.kind != primitive.kind:
        raise ValueError("A construction cannot change primitive family.")
    if item.primitive and topology_signature(item.primitive) != topology_signature(primitive):
        require_topology_edit(session.document, entity)
    session.replace_entities({entity: replace(item, primitive=primitive)})
    tasks.edited(session, {entity})


def topology_signature(primitive: Primitive) -> tuple[Any, ...]:
    from anthroforge.core.construction import cyclic

    curves = tuple((c.id, cyclic(c, primitive)) for c in primitive.curves)
    pieces = tuple((p.id, p.shape, p.sides) for p in primitive.pieces)
    return primitive.samples, primitive.strips, primitive.caps, curves, pieces


def update(session: "Session", entity: str, **options: Any) -> None:
    primitive = definition(session, entity)
    if set(options) - {"samples", "strips", "start", "span", "caps"}:
        raise ValueError("Unknown primitive setting.")
    require_loft_settings(primitive, options)
    if set(options) & {"samples", "strips", "caps"}:
        require_topology_edit(session.document, entity)
    install(session, entity, replace(primitive, **options))


def curve_update(session: "Session", entity: str, curve: str, **options: Any) -> None:
    primitive = definition(session, entity)
    require_loft_settings(primitive, options)
    selected = next(c for c in primitive.curves if c.id == curve)
    if "closed" in options:
        require_topology_edit(session.document, entity)
    if set(options) - {"name", "closed", "matrix", "start", "span", "resolution"}:
        raise ValueError("Unknown curve setting.")
    changed = replace(selected, **codec.tuples(options))
    install(
        session,
        entity,
        replace(primitive, curves=tuple(changed if c.id == curve else c for c in primitive.curves)),
    )


def point_update(session: "Session", entity: str, curve: str, point: str, **options: Any) -> None:
    primitive = definition(session, entity)
    selected = next(c for c in primitive.curves if c.id == curve)
    index = next(i for i, p in enumerate(selected.points) if p.id == point)
    changed = curve_editing.point(session.engine, selected, index, codec.tuples(options))
    points = tuple(changed if p.id == point else p for p in selected.points)
    replace_curve(session, entity, primitive, replace(selected, points=points))


def replace_curve(session: "Session", entity: str, primitive: Primitive, changed: Curve) -> None:
    install(
        session,
        entity,
        replace(
            primitive, curves=tuple(changed if c.id == changed.id else c for c in primitive.curves)
        ),
    )


def point_insert(
    session: "Session", entity: str, curve: str, index: int, point: dict[str, Any]
) -> str:
    primitive = definition(session, entity)
    selected = next(c for c in primitive.curves if c.id == curve)
    if not 0 <= index <= len(selected.points):
        raise ValueError("Point insertion index is outside the curve.")
    added = CurvePoint(**codec.tuples(point))
    points = (*selected.points[:index], added, *selected.points[index:])
    replace_curve(session, entity, primitive, replace(selected, points=points))
    return added.id


def point_remove(session: "Session", entity: str, curve: str, point: str) -> None:
    primitive = definition(session, entity)
    selected = next(c for c in primitive.curves if c.id == curve)
    points = tuple(p for p in selected.points if p.id != point)
    replace_curve(session, entity, primitive, replace(selected, points=points))


def curve_add(session: "Session", entity: str, source: str = "") -> str:
    primitive = definition(session, entity)
    require_topology_edit(session.document, entity)
    curve = straight_curve(0.3)
    if source:
        original = next(c for c in primitive.curves if c.id == source)
        curve = replace(
            original,
            id=curve.id,
            points=tuple(replace(p, id=CurvePoint().id) for p in original.points),
        )
    pieces = primitive.pieces + ((BodyPiece(curve.id),) if primitive.kind == "BODY" else ())
    install(session, entity, replace(primitive, curves=(*primitive.curves, curve), pieces=pieces))
    return curve.id


def curve_remove(session: "Session", entity: str, curve: str) -> None:
    primitive = definition(session, entity)
    require_topology_edit(session.document, entity)
    components = {curve} | {p.id for p in primitive.pieces if p.curve == curve}
    if any(b.target.component in components for b in session.document.entity(entity).deformers):
        raise ValueError("Remove the curve's deformer bindings first.")
    install(
        session,
        entity,
        replace(
            primitive,
            curves=tuple(c for c in primitive.curves if c.id != curve),
            pieces=tuple(p for p in primitive.pieces if p.curve != curve),
        ),
    )


def require_loft_settings(primitive: Primitive, options: dict[str, Any]) -> None:
    if primitive.kind != "LOFT" and set(options) & {"start", "span", "strips", "caps"}:
        raise ValueError("Sampling ranges, strips and caps are loft settings.")


def curve_order(session: "Session", entity: str, curves: list[str]) -> None:
    primitive = definition(session, entity)
    require_topology_edit(session.document, entity)
    lookup = {c.id: c for c in primitive.curves}
    if set(curves) != set(lookup) or len(curves) != len(lookup):
        raise ValueError("Curve order must include every owned curve exactly once.")
    install(session, entity, replace(primitive, curves=tuple(lookup[c] for c in curves)))


def piece_update(session: "Session", entity: str, piece: str, **options: Any) -> None:
    primitive = definition(session, entity)
    selected = next(p for p in primitive.pieces if p.id == piece)
    if set(options) & {"shape", "sides"}:
        require_topology_edit(session.document, entity)
    if "id" in options or "curve" in options:
        raise ValueError("Piece identity and owned curve cannot be changed.")
    changed = replace(selected, **options)
    install(
        session,
        entity,
        replace(primitive, pieces=tuple(changed if p.id == piece else p for p in primitive.pieces)),
    )


def thickness(session: "Session", entity: str, remove: bool = False, **options: Any) -> None:
    item = session.editable(entity)
    if item.thickness is None or remove or set(options) & {"enabled", "rim", "rim_only", "flip"}:
        require_topology_edit(session.document, entity)
    changed = None if remove else replace(item.thickness or Thickness(), **codec.tuples(options))
    session.replace_entities({entity: replace(item, thickness=changed)})
    tasks.edited(session, {entity})


def inspect(session: "Session", entity: str) -> dict[str, Any]:
    from .construction_policy import topology_dependents

    item = session.document.entity(entity)
    return {
        "primitive": asdict(item.primitive) if item.primitive else None,
        "deformers": [asdict(d) for d in item.deformers],
        "result": asdict(item.result),
        "topology_dependents": topology_dependents(session.document, entity),
    }
