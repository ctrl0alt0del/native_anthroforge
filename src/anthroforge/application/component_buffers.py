"""Shared native coordinate resolution for UI and authoring component reads."""

from typing import Any

from anthroforge.core.component_reads import ComponentBuffer
from anthroforge.core.construction import Curve, body_closed
from anthroforge.core.primitive_sampling import count
from anthroforge.native import bodies, components, construction
from anthroforge.native.geometry_modifiers import subdivide
from anthroforge.native.scene import entity_frame

from . import curve_sources
from .component_restrictions import curve_reason
from .control_frames import display_frame


def buffer(
    session: Any, local: Any, frame: Any, common: Any, references: Any = (), owner: Any = None
) -> Any:
    world = components.transformed(session.engine, local, frame)
    world.flags.writeable = False
    return ComponentBuffer(
        local,
        world,
        tuple(frame),
        tuple(common.items()),
        tuple(tuple(ref.items()) for ref in references),
        owner,
    )


def curve_frame(session: Any, item: Any, curve: Any = None) -> Any:
    if isinstance(item, Curve):
        return curve_sources.world(session.engine, session.document, item.id)
    frame = entity_frame(session.engine, item)
    return construction.matrix(session.engine, frame, curve.matrix) if curve else frame


def curve(session: Any, item: Any, value: Any) -> Any:
    records = construction.resolved_curve(session.engine, value)
    order = [3, 4, 5, 0, 1, 2, 6, 7, 8] if value.engine == "BEZIER" else [0, 1, 2]
    local = records[:, order].reshape((-1, 3))
    local.flags.writeable = False
    return buffer(
        session, local, curve_frame(session, item, value), {}, curve_refs(session, item, value)
    )


def curve_refs(session: Any, item: Any, value: Any) -> Any:
    parts = ("left", "position", "right") if value.engine == "BEZIER" else ("position",)
    return [
        curve_reference(session, item, value, p, part, i)
        for i, p in enumerate(value.points)
        for part in parts
    ]


def curve_reference(session: Any, item: Any, value: Any, point: Any, part: str, index: int) -> Any:
    reason = curve_reason(session, value, point, part)
    return dict(
        owner=item.id,
        curve=value.id,
        point=point.id,
        part=part,
        index=index * 3 + ("left", "position", "right").index(part),
        readonly=bool(reason),
        reason=reason,
        junction=point.junction,
    )


def control(session: Any, item: Any) -> Any:
    local = item.points if item.kind == "LATTICE" else ((0, 0, 0),)
    ref = dict(owner=item.id, part="lattice" if item.kind == "LATTICE" else "control")
    return buffer(session, local, display_frame(session, item), ref)


def imported(session: Any, item: Any) -> Any:
    mesh = session.assets[item.primitive.source].mesh
    return buffer(
        session,
        mesh.array(0),
        entity_frame(session.engine, item),
        dict(owner=item.id, part="vertex"),
        owner=mesh,
    )


def base(session: Any, item: Any, piece: Any) -> Any:
    density = count(session.document.entity(item.id).primitive, piece.curve)
    value = next(c for c in item.primitive.curves if c.id == piece.curve)
    mesh = bodies.base(session.engine, piece, density, body_closed(piece, value, item.primitive), 0)
    return base_buffer(session, item, value, piece, mesh)


def base_buffer(session: Any, item: Any, value: Any, piece: Any, mesh: Any) -> Any:
    mesh = subdivide(mesh, piece.subdivision)
    return buffer(
        session,
        mesh.array(0),
        curve_frame(session, item, value),
        dict(owner=item.id, piece=piece.id, part="base"),
        owner=mesh,
    )
