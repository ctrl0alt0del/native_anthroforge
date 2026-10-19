"""Preserve construction objects and their visible frames when removing an anatomical owner."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Control, Curve
from anthroforge.core.curve_consumption import uses, with_uses
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.object_registry import Construction, SceneObject
from anthroforge.core.results import Port
from anthroforge.core.surfaces import Surface
from anthroforge.native.construction import matrix

from . import curve_consumers, curve_sources
from .object_revisions import authored

if TYPE_CHECKING:
    from .session import Session


def require_removable(session: "Session", item: Construction) -> None:
    if isinstance(item, Curve) and any(p.junction for p in item.points):
        raise ValueError("Detach shared junctions before deleting this curve.")
    users = curve_sources.consumers(session.document, {item.id})
    if users:
        raise ValueError("Object is referenced by consumers: " + ", ".join(sorted(users)))


def install(
    session: "Session",
    entities: tuple[SCP, ...],
    controls: tuple[Control, ...],
    objects: tuple[Construction, ...],
) -> None:
    from .dependent_tasks import changed

    ports = changed_inputs(session, controls, objects)
    session.scheduler.invalidate_ports(ports)
    session.replace_document(entities=entities, controls=controls, objects=objects)
    changed(session, ports, published=False)


def changed_inputs(
    session: "Session", controls: tuple[Control, ...], objects: tuple[Construction, ...]
) -> set[Port]:
    from .object_revisions import changed_ports

    before = session.document.registry.records
    sources = session.document.registry.construction
    ports = set().union(*(changed_ports(sources[o.id], o) for o in objects))
    ports.update(Port(c.id, "control") for c in controls if c != before[c.id])
    return ports


def retain_objects(
    session: "Session", removed: SceneObject, parent: SceneObject | None
) -> tuple[Construction, ...]:
    for item in session.document.objects:
        if isinstance(item, Fiber) and (
            removed.id in item.supports or any(b.target == removed.id for b in item.bindings)
        ):
            raise ValueError(
                "Rebind the dependent fiber before deleting its attachment target: " + item.name
            )
    return tuple(retain_object(session, item, removed, parent) for item in session.document.objects)


def retain_object(
    session: "Session", item: Construction, removed: SceneObject, parent: SceneObject | None
) -> Construction:
    if isinstance(item, Surface):
        item = rebase_uses(session, item, removed.id)
    item = without_obstacle(item, removed.id)
    owners = tuple(key for key in item.owners if key != removed.id)
    if item.parent != removed.id:
        return replace(item, owners=owners) if owners != item.owners else item
    absolute = curve_sources.world(session.engine, session.document, item.id)
    frame = parent_frame(session, parent)
    local = matrix(session.engine, frame, absolute, relative=True)
    changed = replace(item, owners=owners, parent=parent.id if parent else "", matrix=local)
    return authored(item, changed)


def without_obstacle(item: Construction, removed: str) -> Construction:
    from anthroforge.core.curve_engines import RoutingSettings

    if not isinstance(item, Curve) or not isinstance(item.engine_settings, RoutingSettings):
        return item
    config = item.engine_settings
    settings = replace(
        config,
        obstacles=tuple(k for k in config.obstacles if k != removed),
        excluded_obstacles=tuple(k for k in config.excluded_obstacles if k != removed),
    )
    return authored(item, replace(item, engine_settings=settings)) if settings != config else item


def parent_frame(session: "Session", parent: SceneObject | None) -> tuple[float, ...]:
    from anthroforge.core.entities import IDENTITY

    if parent is None:
        return IDENTITY
    if parent.id not in session.document.registry.records:
        return parent.matrix
    return curve_sources.world(session.engine, session.document, parent.id)


def retain_frames(session: "Session", entities: tuple[SCP, ...], removed: str) -> tuple[SCP, ...]:
    return tuple(rebase_uses(session, item, removed) for item in entities)


def rebase_uses[T: SCP | Surface](session: "Session", item: T, removed: str) -> T:
    previous = uses(item)
    if not previous:
        return item
    sources = tuple(
        rebase_use(session, use) if use.reference_frame == removed else use for use in previous
    )
    return curve_consumers.revised(item, with_uses(item, sources))


def rebase_use(session: "Session", use: CurveUse) -> CurveUse:
    return replace(
        use,
        reference_frame="",
        matrix=curve_sources.use_frame(session.engine, session.document, use),
        bind_matrix=curve_sources.world(session.engine, session.document, use.curve),
    )
