"""Resolved tissue controls and material field points, independent of presentation."""

from typing import Any

from . import component_buffers, tissue_fields
from .object_frames import Frames
from .tissue_part_operations import control_value, selected


def controls(session: Any, item: Any, context: Any) -> Any:
    part, side = context.get("part", "main"), context.get("side", "a")
    if side not in ("a", "b"):
        raise ValueError("Tissue side must be a or b.")
    inflation = getattr(selected(item, part), side).inflation
    if inflation.mode != "CTRL_POINT" or (side == "b" and not item.both_sides):
        return ()
    local = inflation.control or control_value(session, item, part)
    ref = dict(owner=item.id, piece=part, side=side, part="tissue_control", index=int(side == "b"))
    frame = Frames(session.engine, session.document).world(item.id)
    return (component_buffers.buffer(session, (local,), frame, ref, (ref,)),)


def fields(session: Any, item: Any, context: Any) -> Any:
    field = next((f for f in item.fields if f.name == context.get("field")), None)
    if field is None:
        return ()
    tissue_fields.validate(session.resources, item, field.domain)
    local = tissue_fields.positions(session, item, field.domain)
    refs = tuple(reference(item, field, i, w) for i, w in enumerate(field.values))
    frame = Frames(session.engine, session.document).world(item.id)
    local.flags.writeable = False
    return (component_buffers.buffer(session, local, frame, {}, refs),)


def reference(item: Any, field: Any, index: Any, weight: Any) -> Any:
    return dict(
        owner=item.id,
        piece=field.topology + field.name,
        part="field",
        index=index,
        field=field.name,
        topology=field.topology,
        weight=weight,
    )
