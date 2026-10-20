"""Create a curve and its first shared junction as one document operation."""

from dataclasses import replace
from typing import Any

from anthroforge.core import curve_engines
from anthroforge.core.junctions import Junction
from anthroforge.native import curve_editing

from . import dependent_tasks, junction_edits, junction_operations, object_operations, path_tasks
from .object_creation import require_owner


def create(
    session: Any,
    source: dict[str, str],
    points: list[dict[str, Any]],
    name: str = "Branch curve",
    owner: str = "",
    engine: str = "BEZIER",
    closed: bool = False,
) -> str:
    item, ref = junction_operations.member(session, source)
    curve = definition(session, name, points, owner, engine, closed)
    return connected(session, item, ref, curve)


def definition(session: Any, name: str, points: Any, owner: str, engine: str, closed: bool) -> Any:
    if owner:
        require_owner(session, owner)
    curve = object_operations.new_curve(name, points, "", owner)
    return replace(curve, engine_settings=curve_engines.decode(engine), closed=closed)


def connected(session: Any, item: Any, ref: Any, curve: Any) -> str:
    shared = junction_edits.point(item, ref.point).junction
    junction = next((j for j in session.document.junctions if j.id == shared), Junction(ref))
    world = junction_edits.world_position(session, item, ref.point)
    first = curve_editing.point(session.engine, curve, 0, dict(position=world))
    curve = replace(curve, points=(replace(first, junction=junction.id), *curve.points[1:]))
    return install(session, item, curve, junction, bool(shared))


def install(session: Any, source: Any, curve: Any, junction: Junction, existing: bool) -> str:
    changes = {} if existing else tagged_source(session, source, junction)
    objects = tuple(changes.get(o.id, o) for o in session.document.objects) + (curve,)
    junctions = session.document.junctions + (() if existing else (junction,))
    replace(session.document, objects=objects, junctions=junctions)
    ports = junction_operations.changed_ports(session, changes)
    session.scheduler.invalidate_ports(ports)
    session.replace_document(objects=objects, junctions=junctions)
    dependent_tasks.changed(session, ports, published=False)
    path_tasks.request(session, curve.id)
    return str(curve.id)


def tagged_source(session: Any, source: Any, junction: Junction) -> dict[str, Any]:
    before = session.document.object(source.id)
    points = tuple(
        replace(p, junction=junction.id) if p.id == junction.source.point else p
        for p in before.points
    )
    changed = junction_edits.revised(session, before, replace(before, points=points))
    return {source.id: changed}
