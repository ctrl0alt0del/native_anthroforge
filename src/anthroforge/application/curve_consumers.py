"""Live primitive sources and no-jump consumer transform modes."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import BodyPiece, Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.native.construction import matrix
from anthroforge.native.scene import entity_frame

from . import construction_tasks, curve_sources
from .operations import parent_for, require_name
from .primitive_operations import finish_create, new_entity

if TYPE_CHECKING:
    from .session import Session


def from_curves(
    session: "Session",
    curves: list[str],
    kind: str,
    parent: str = "",
    name: str = "Primitive",
    shape: str = "CAPSULE",
) -> str:
    entity = new_entity(require_name(name), parent_for(session, parent), None)
    primitive = source_definition(session, entity, curves, kind, shape)
    session.replace_document(
        entities=(*session.document.entities, replace(entity, primitive=primitive))
    )
    return finish_create(session, entity)


def source_definition(
    session: "Session", entity: SCP, curves: list[str], kind: str, shape: str
) -> Primitive:
    uses = tuple(bind(session, entity, key) for key in curves)
    pieces = tuple(BodyPiece(key, shape) for key in curves) if kind == "BODY" else ()
    return Primitive(kind, curves=uses, pieces=pieces)


def ancestors(document: Document, key: str) -> tuple[str, ...]:
    result = []
    while key:
        result.append(key)
        item = document.object(key)
        key = getattr(item, "parent", "")
    return tuple(result)


def bind(session: "Session", entity: SCP, key: str) -> CurveUse:
    curve = curve_sources.source(session.document, key)
    common = common_frame(session.document, entity, curve.parent)
    absolute = curve_sources.world(session.engine, session.document, key)
    frame = curve_sources.world(session.engine, session.document, common)
    local = matrix(session.engine, entity_frame(session.engine, entity), absolute, relative=True)
    bound = matrix(session.engine, frame, absolute, relative=True)
    return CurveUse(key, matrix=local, bind_matrix=bound, reference_frame=common)


def common_frame(document: Document, entity: SCP, source_parent: str) -> str:
    owners = set(ancestors(document, entity.parent)) | {entity.id}
    return next((p for p in ancestors(document, source_parent) if p in owners), "")


def transform_mode(session: "Session", entity: str, curve: str, mode: str) -> None:
    item, use = selected_use(session, entity, curve)
    install_use(session, item, rebound_use(session, use, mode))


def reverse(session: "Session", entity: str, curve: str, enabled: bool) -> None:
    item, use = selected_use(session, entity, curve)
    install_use(session, item, replace(use, reverse=enabled))


def selected_use(session: "Session", entity: str, curve: str) -> tuple[SCP, CurveUse]:
    item = session.editable(entity)
    if not isinstance(item.primitive, Primitive):
        raise ValueError("Select a constructed primitive.")
    use = next((u for u in item.primitive.curves if u.curve == curve), None)
    if use is None:
        raise ValueError("Primitive does not reference this curve.")
    return item, use


def install_use(session: "Session", item: SCP, changed: CurveUse) -> None:
    assert isinstance(item.primitive, Primitive)
    uses = tuple(changed if u.curve == changed.curve else u for u in item.primitive.curves)
    session.replace_entities(
        {item.id: replace(item, primitive=replace(item.primitive, curves=uses))}
    )
    construction_tasks.edited(session, {item.id})


def rebound_use(session: "Session", use: CurveUse, mode: str) -> CurveUse:
    local = curve_sources.use_frame(session.engine, session.document, use)
    reference = curve_sources.world(session.engine, session.document, use.reference_frame)
    absolute = curve_sources.world(session.engine, session.document, use.curve)
    bound = matrix(session.engine, reference, absolute, relative=True)
    return replace(use, mode=mode, matrix=local, bind_matrix=bound)
