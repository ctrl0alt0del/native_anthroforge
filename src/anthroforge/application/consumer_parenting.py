"""Rebind relative consumer frames atomically when ordinary parenting changes."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.curve_consumption import uses, with_uses
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.surfaces import Surface
from anthroforge.native.construction import matrix

from . import curve_consumers, curve_sources

if TYPE_CHECKING:
    from .session import Session


def rebind(session: "Session", after: Document, target: str) -> Document:
    entities = tuple(rebind_consumer(session, after, item, target) for item in after.entities)
    objects = tuple(
        rebind_consumer(session, after, item, target) if isinstance(item, Surface) else item
        for item in after.objects
    )
    return replace(after, entities=entities, objects=objects)


def rebind_consumer[T: SCP | Surface](
    session: "Session", after: Document, item: T, target: str
) -> T:
    previous = uses(item)
    if not previous:
        return item
    sources = tuple(
        rebind_use(session, after, item, use) if affected(after, item, use, target) else use
        for use in previous
    )
    return curve_consumers.revised(item, with_uses(item, sources))


def affected(document: Document, item: SCP | Surface, use: CurveUse, target: str) -> bool:
    return target in (
        *curve_consumers.ancestors(document, use.curve),
        *curve_consumers.ancestors(document, item.id),
    )


def rebind_use(session: "Session", after: Document, item: SCP | Surface, use: CurveUse) -> CurveUse:
    source = curve_sources.source(after, use.curve)
    common = curve_consumers.common_frame(after, item, source.parent)
    frame = curve_sources.world(session.engine, after, common)
    absolute = curve_sources.world(session.engine, after, source.id)
    bound = matrix(session.engine, frame, absolute, relative=True)
    local = curve_sources.use_frame(session.engine, session.document, use)
    return replace(use, reference_frame=common, bind_matrix=bound, matrix=local)
