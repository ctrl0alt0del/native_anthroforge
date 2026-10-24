"""Construction object commands share transactions and native transform boundaries."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core import curve_engines
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_shapes import reshaped
from anthroforge.core.object_registry import Authored
from anthroforge.core.objects import ObjectRecord
from anthroforge.native import curve_editing

from . import (
    curve_edit_state,
    curve_sources,
    dependent_tasks,
    object_revisions,
    path_tasks,
)
from .construction_policy import require_topology_edit
from .object_removal import install as install_removal
from .operations import require_name
from .transform_policy import require_object_transform

if TYPE_CHECKING:
    from .session import Session


def editable(session: "Session", target: str) -> Authored:
    from .workspace_policy import included
    from anthroforge.core.mirroring import require_source

    require_source(target)
    if session.waiting_save:
        raise ValueError("Editing is blocked while waiting to save.")
    item = session.document.object(target)
    if not isinstance(item, ObjectRecord):
        raise ValueError("This operation requires a construction object.")
    if not included(session.document, session.workspace, target):
        raise ValueError("This construction object is outside the focused workspace.")
    return item


def install(session: "Session", item: Authored, **related: Any) -> None:
    from . import junction_operations

    before = editable(session, item.id)
    if junction_operations.edit(session, item):
        return
    item = curve_edit_state.prepare(session, before, item)
    changed = object_revisions.authored(before, item)
    if changed is before:
        return
    ports = object_revisions.changed_ports(before, changed)
    session.scheduler.invalidate_ports(ports)
    install_state(session, before, changed, **related)
    dependent_tasks.changed(session, ports, published=False)


def install_state(session: "Session", before: Authored, changed: Authored, **related: Any) -> None:
    from . import consumer_parenting

    existing = related.pop("objects", session.document.objects)
    objects = tuple(changed if o.id == changed.id else o for o in existing)
    after = replace(session.document, objects=objects, **related)
    if changed.parent != before.parent:
        after = consumer_parenting.rebind(session, after, changed.id)
    session.replace_document(objects=after.objects, entities=after.entities, **related)


def rename(session: "Session", target: str, name: str) -> None:
    install(session, replace(editable(session, target), name=require_name(name)))


def transform(session: "Session", target: str, values: list[float], world: bool = False) -> None:
    from anthroforge.native.construction import matrix

    item = editable(session, target)
    require_object_transform(item)
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
    settings: dict[str, Any] | None = None,
    projection: Any = None,
) -> str:
    curve = definition(name, points, parent, owner, engine, settings, closed)
    curve = replace(curve, matrix=creation_frame(session, parent, values))
    return install_placed_curve(session, curve, projection)


def definition(
    name: str, points: Any, parent: str, owner: str, engine: str, settings: Any, closed: bool
) -> Curve:
    config = curve_engines.decode(engine, settings)
    return replace(new_curve(name, points, parent, owner), engine_settings=config, closed=closed)


def install_placed_curve(session: "Session", curve: Curve, projection: Any) -> str:
    from .snap_tasks import confirm_samples

    result = install_new_curve(session, curve)
    confirm_samples(session, result, projection)
    return result


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

    item = curve_edit_state.current(session, editable(session, curve))
    if not isinstance(item, Curve):
        raise ValueError("Select a curve or fiber.")
    if set(options) - {"name", "closed", "resolution"}:
        raise ValueError("Unknown curve property; engine conversion is a separate operation.")
    if set(options) & {"closed", "resolution"}:
        for consumer in curve_sources.consumers(session.document, {curve}):
            require_topology_edit(session.document, consumer)
    install(session, updated_curve(item, tuples(options)))


def updated_curve(item: Curve, options: dict[str, Any]) -> Curve:
    settings = dict(options)
    if "resolution" in settings:
        config = curve_engines.decode(item.engine, dict(resolution=settings.pop("resolution")))
        settings["engine_settings"] = config
    return reshaped(item, **settings)


def edit_point(session: "Session", curve: str, point: str, **options: Any) -> None:
    from .construction_codec import tuples

    item = curve_edit_state.current(session, editable(session, curve))
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

    item = session.document.registry.authored.get(target)
    if item is None:
        raise ValueError("Unknown construction object.")
    return {
        **encode(item),
        "consumers": sorted(curve_sources.consumers(session.document, {target})),
    }


def delete(session: "Session", target: str) -> None:
    from .control_frames import remove_supports
    from .object_removal import require_removable, retain_frames, retain_objects

    item = editable(session, target)
    require_removable(session, item)
    parent = session.document.object(item.parent) if item.parent else None
    objects = tuple(o for o in retain_objects(session, item, parent) if o.id != target)
    entities = retain_frames(session, session.document.entities, target)
    session.scheduler.invalidate({target})
    install_removal(
        session, objects=objects, entities=entities, controls=remove_supports(session, {target})
    )
