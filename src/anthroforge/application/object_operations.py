"""Construction object commands share transactions and native transform boundaries."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.object_registry import Construction
from anthroforge.core.objects import ConstructionObject
from anthroforge.native import curve_editing

from . import construction_tasks, curve_sources, dependencies, object_revisions, path_tasks
from .construction_policy import require_topology_edit
from .operations import require_name

if TYPE_CHECKING:
    from .session import Session


def editable(session: "Session", target: str) -> Construction:
    from .workspace_policy import included

    if session.waiting_save:
        raise ValueError("Editing is blocked while waiting to save.")
    item = session.document.object(target)
    if not isinstance(item, ConstructionObject):
        raise ValueError("This operation requires a construction object.")
    if not included(session.document, session.workspace, target):
        raise ValueError("This construction object is outside the focused workspace.")
    return item


def install(session: "Session", item: Construction) -> None:
    before = editable(session, item.id)
    changed = object_revisions.authored(before, item)
    if changed is before:
        return
    ports = object_revisions.changed_ports(before, changed)
    session.scheduler.invalidate_ports(ports)
    install_state(session, before, changed)
    path_tasks.edited(session, ports)
    construction_tasks.edited(session, dependencies.affected(session.document, ports))


def install_state(session: "Session", before: Construction, changed: Construction) -> None:
    from . import consumer_parenting

    objects = tuple(changed if o.id == changed.id else o for o in session.document.objects)
    entities = session.document.entities
    if changed.parent != before.parent:
        after = replace(session.document, objects=objects)
        entities = consumer_parenting.entities(session, after, changed.id)
    session.replace_document(objects=objects, entities=entities)


def rename(session: "Session", target: str, name: str) -> None:
    install(session, replace(editable(session, target), name=require_name(name)))


def transform(session: "Session", target: str, values: list[float], world: bool = False) -> None:
    from anthroforge.native.construction import matrix

    item = editable(session, target)
    frame = session.engine.transform(values)
    if world:
        parent = curve_sources.world(session.engine, session.document, item.parent)
        frame = matrix(session.engine, parent, frame, relative=True)
    install(session, replace(item, matrix=frame))


def reparent(session: "Session", target: str, parent: str = "") -> None:
    from anthroforge.native.construction import matrix

    item = editable(session, target)
    absolute = curve_sources.world(session.engine, session.document, target)
    frame = curve_sources.world(session.engine, session.document, parent)
    local = matrix(session.engine, frame, absolute, relative=True)
    install(session, replace(item, parent=parent, matrix=local))


def create_curve(
    session: "Session",
    name: str = "Curve",
    points: list[dict[str, Any]] | None = None,
    parent: str = "",
    owner: str = "",
    engine: str = "BEZIER",
    closed: bool = False,
    values: list[float] | None = None,
) -> str:
    curve = replace(new_curve(name, points, parent, owner), engine=engine, closed=closed)
    curve = replace(curve, matrix=creation_frame(session, parent, values))
    return install_new_curve(session, curve)


def creation_frame(
    session: "Session", parent: str, values: list[float] | None
) -> tuple[float, ...]:
    from anthroforge.native.construction import matrix

    from .object_creation import require_parent

    require_parent(session, parent)
    if values is not None:
        return session.engine.transform(values)
    absolute = session.engine.transform([*session.workspace.cursor, 0, 0, 0, 1, 1, 1])
    frame = curve_sources.world(session.engine, session.document, parent)
    return matrix(session.engine, frame, absolute, relative=True)


def install_new_curve(session: "Session", curve: Curve) -> str:
    owner = curve.owners[0] if curve.owners else ""
    if owner:
        session.editable(owner)
    session.replace_document(objects=(*session.document.objects, curve))
    path_tasks.request(session, curve.id)
    return curve.id


def new_curve(name: str, points: list[dict[str, Any]] | None, parent: str, owner: str) -> Curve:
    from .construction_codec import tuples
    from .primitive_operations import straight_curve

    authored = (
        tuple(CurvePoint(**tuples(p)) for p in points)
        if points is not None
        else straight_curve().points
    )
    return Curve(authored, name=require_name(name), parent=parent, owners=(owner,) if owner else ())


def edit_curve(session: "Session", curve: str, **options: Any) -> None:
    from .construction_codec import tuples

    item = editable(session, curve)
    if not isinstance(item, Curve):
        raise ValueError("Select a curve or fiber.")
    if set(options) - {"name", "closed", "resolution"}:
        raise ValueError("Unknown curve property; engine conversion is a separate operation.")
    if set(options) & {"closed", "resolution"}:
        for consumer in curve_sources.consumers(session.document, {curve}):
            require_topology_edit(session.document, consumer)
    install(session, replace(item, **tuples(options)))


def edit_point(session: "Session", curve: str, point: str, **options: Any) -> None:
    from .construction_codec import tuples

    item = editable(session, curve)
    if not isinstance(item, Curve):
        raise ValueError("Select a curve or fiber.")
    index = next((i for i, p in enumerate(item.points) if p.id == point), -1)
    if index < 0:
        raise ValueError("Unknown authored curve point.")
    changed = curve_editing.point(session.engine, item, index, tuples(options))
    points = tuple(changed if p.id == point else p for p in item.points)
    install(session, replace(item, points=points))


def inspect(session: "Session", target: str) -> dict[str, Any]:
    from .object_codec import encode

    item = session.document.registry.construction.get(target)
    if item is None:
        raise ValueError("Unknown construction object.")
    return {
        **encode(item),
        "consumers": sorted(curve_sources.consumers(session.document, {target})),
    }


def delete(session: "Session", target: str) -> None:
    from .object_removal import retain_frames, retain_objects

    item = editable(session, target)
    users = curve_sources.consumers(session.document, {target})
    if users:
        raise ValueError("Object is referenced by consumers: " + ", ".join(sorted(users)))
    parent = session.document.object(item.parent) if item.parent else None
    objects = tuple(o for o in retain_objects(session, item, parent) if o.id != target)
    entities = retain_frames(session, session.document.entities, target)
    session.scheduler.invalidate({target})
    session.replace_document(objects=objects, entities=entities)
