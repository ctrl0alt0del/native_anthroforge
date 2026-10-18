"""Rebind relative consumer frames atomically when ordinary parenting changes."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.native.construction import matrix

from . import curve_consumers, curve_sources
from .entity_revisions import authored

if TYPE_CHECKING:
    from .session import Session


def entities(session: "Session", after: Document, target: str) -> tuple[SCP, ...]:
    return tuple(rebind_entity(session, after, item, target) for item in after.entities)


def rebind_entity(session: "Session", after: Document, item: SCP, target: str) -> SCP:
    if not isinstance(item.primitive, Primitive):
        return item
    uses = tuple(
        rebind_use(session, after, item, use) if affected(after, use, target) else use
        for use in item.primitive.curves
    )
    return authored(item, replace(item, primitive=replace(item.primitive, curves=uses)))


def affected(document: Document, use: CurveUse, target: str) -> bool:
    return target in curve_consumers.ancestors(document, use.curve)


def rebind_use(session: "Session", after: Document, item: SCP, use: CurveUse) -> CurveUse:
    source = curve_sources.source(after, use.curve)
    common = curve_consumers.common_frame(after, item, source.parent)
    frame = curve_sources.world(session.engine, after, common)
    absolute = curve_sources.world(session.engine, after, source.id)
    bound = matrix(session.engine, frame, absolute, relative=True)
    local = curve_sources.use_frame(session.engine, session.document, use)
    return replace(use, reference_frame=common, bind_matrix=bound, matrix=local)
