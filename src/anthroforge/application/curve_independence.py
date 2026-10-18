"""Detach a consumer from shared authored points without changing the visible geometry."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Curve, Primitive
from anthroforge.core.entities import SCP
from anthroforge.core.surfaces import Surface

from . import construction_copy, construction_tasks, curve_consumers, curve_copy, curve_sources
from .curve_copy_resources import Copies

if TYPE_CHECKING:
    from .session import Session


def make_independent(session: "Session", entity: str, curve: str) -> str:
    from .surface_independence import independent

    item, _ = curve_consumers.selected_use(session, entity, curve)
    if isinstance(item, Surface) and item.branches:
        copied_id = independent(session, item, curve)
        construction_tasks.edited(session, {entity})
        return copied_id
    source = curve_sources.source(session.document, curve)
    identities = curve_copy.mapping(source)
    copied = Copies(session.resources, identities).record(source)
    install(session, item, copied, identities)
    construction_tasks.edited(session, {entity})
    return copied.id


def install(
    session: "Session", item: SCP | Surface, copied: Curve, identities: dict[str, str]
) -> None:
    changed = curve_consumers.revised(item, remapped(item, identities))
    session.scheduler.invalidate({item.id})
    if isinstance(changed, SCP):
        entities = tuple(changed if e.id == item.id else e for e in session.document.entities)
        session.replace_document(entities=entities, objects=(*session.document.objects, copied))
    else:
        objects = tuple(changed if o.id == item.id else o for o in session.document.objects)
        session.replace_document(objects=(*objects, copied))


def remapped(item: SCP | Surface, identities: dict[str, str]) -> SCP | Surface:
    if isinstance(item, Surface):
        return remapped_surface(item, identities)
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


def remapped_surface(item: Surface, identities: dict[str, str]) -> Surface:
    from .surface_independence import remapped_branch

    return replace(
        item,
        curves=tuple(replace(u, curve=identities.get(u.curve, u.curve)) for u in item.curves),
        alignment=tuple(replace(a, point=identities.get(a.point, a.point)) for a in item.alignment),
        main=tuple(identities.get(key, key) for key in item.main),
        branches=tuple(remapped_branch(b, identities) for b in item.branches),
    )
