"""Detach a consumer from shared authored points without changing the visible geometry."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Curve, Primitive
from anthroforge.core.entities import SCP

from . import construction_copy, construction_tasks, curve_copy, curve_sources
from .curve_copy_resources import Copies

if TYPE_CHECKING:
    from .session import Session


def make_independent(session: "Session", entity: str, curve: str) -> str:
    item = session.editable(entity)
    if not isinstance(item.primitive, Primitive) or curve not in {
        u.id for u in item.primitive.curves
    }:
        raise ValueError("Primitive does not reference this curve.")
    source = curve_sources.source(session.document, curve)
    identities = curve_copy.mapping(source)
    copied = Copies(session.resources, identities).record(source)
    install(session, item, copied, identities)
    construction_tasks.edited(session, {entity})
    return copied.id


def install(session: "Session", item: SCP, copied: Curve, identities: dict[str, str]) -> None:
    from .entity_revisions import authored

    changed = authored(item, remapped(item, identities))
    session.scheduler.invalidate({item.id})
    entities = tuple(changed if e.id == item.id else e for e in session.document.entities)
    session.replace_document(entities=entities, objects=(*session.document.objects, copied))


def remapped(item: SCP, identities: dict[str, str]) -> SCP:
    assert isinstance(item.primitive, Primitive)
    uses = tuple(
        replace(use, curve=identities.get(use.curve, use.curve)) for use in item.primitive.curves
    )
    pieces = tuple(
        replace(p, curve=identities.get(p.curve, p.curve)) for p in item.primitive.pieces
    )
    ids = {**{b.id: b.id for b in item.deformers}, **identities}
    deformers = tuple(construction_copy.binding(b, ids) for b in item.deformers)
    return replace(
        item, primitive=replace(item.primitive, curves=uses, pieces=pieces), deformers=deformers
    )
