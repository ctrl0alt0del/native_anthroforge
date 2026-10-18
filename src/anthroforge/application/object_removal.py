"""Preserve construction objects and their visible frames when removing an anatomical owner."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.object_registry import Construction, SceneObject
from anthroforge.native.construction import matrix

from . import curve_sources
from .object_revisions import authored

if TYPE_CHECKING:
    from .session import Session


def retain_objects(
    session: "Session", removed: SCP | Construction, parent: SceneObject | None
) -> tuple[Construction, ...]:
    for item in session.document.objects:
        if isinstance(item, Fiber) and any(b.target == removed.id for b in item.bindings):
            raise ValueError(
                "Rebind the dependent fiber before deleting its attachment target: " + item.name
            )
    return tuple(retain_object(session, item, removed, parent) for item in session.document.objects)


def retain_object(
    session: "Session", item: Construction, removed: SCP | Construction, parent: SceneObject | None
) -> Construction:
    owners = tuple(key for key in item.owners if key != removed.id)
    if item.parent != removed.id:
        return replace(item, owners=owners) if owners != item.owners else item
    absolute = curve_sources.world(session.engine, session.document, item.id)
    frame = parent_frame(session, parent)
    local = matrix(session.engine, frame, absolute, relative=True)
    changed = replace(item, owners=owners, parent=parent.id if parent else "", matrix=local)
    return authored(item, changed)


def parent_frame(session: "Session", parent: SceneObject | None) -> tuple[float, ...]:
    from anthroforge.core.entities import IDENTITY

    if parent is None:
        return IDENTITY
    if parent.id not in session.document.registry.records:
        return parent.matrix
    return curve_sources.world(session.engine, session.document, parent.id)


def retain_frames(session: "Session", entities: tuple[SCP, ...], removed: str) -> tuple[SCP, ...]:
    return tuple(rebase_uses(session, item, removed) for item in entities)


def rebase_uses(session: "Session", item: SCP, removed: str) -> SCP:
    primitive = item.primitive
    if not isinstance(primitive, Primitive):
        return item
    uses = tuple(
        rebase_use(session, use) if use.reference_frame == removed else use
        for use in primitive.curves
    )
    return (
        replace(item, primitive=replace(primitive, curves=uses))
        if uses != primitive.curves
        else item
    )


def rebase_use(session: "Session", use: CurveUse) -> CurveUse:
    return replace(
        use,
        reference_frame="",
        matrix=curve_sources.use_frame(session.engine, session.document, use),
        bind_matrix=curve_sources.world(session.engine, session.document, use.curve),
    )
