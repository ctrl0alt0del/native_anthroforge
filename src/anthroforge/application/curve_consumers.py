"""Live primitive sources and no-jump consumer transform modes."""

from dataclasses import replace
from typing import TYPE_CHECKING, cast

from anthroforge.core.construction import BodyPiece, Primitive
from anthroforge.core.curve_consumption import uses, with_uses
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.surfaces import Surface
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
    while key and key not in result:
        result.append(key)
        item = document.object(key)
        key = getattr(item, "parent", "") or getattr(item, "follow", "")
    return tuple(result)


def bind(session: "Session", entity: SCP | Surface, key: str) -> CurveUse:
    curve = curve_sources.source(session.document, key)
    common = common_frame(session.document, entity, curve.parent)
    absolute = curve_sources.world(session.engine, session.document, key)
    frame = curve_sources.world(session.engine, session.document, common)
    local = matrix(session.engine, consumer_frame(session, entity), absolute, relative=True)
    bound = matrix(session.engine, frame, absolute, relative=True)
    return CurveUse(key, matrix=local, bind_matrix=bound, reference_frame=common)


def common_frame(document: Document, entity: SCP | Surface, source_parent: str) -> str:
    owners = set(ancestors(document, entity.parent)) | {entity.id}
    return next((p for p in ancestors(document, source_parent) if p in owners), "")


def consumer_frame(session: "Session", item: SCP | Surface) -> tuple[float, ...]:
    if isinstance(item, SCP):
        return entity_frame(session.engine, item)
    parent = curve_sources.world(session.engine, session.document, item.parent)
    return matrix(session.engine, parent, item.matrix)


def transform_mode(session: "Session", entity: str, curve: str, mode: str) -> None:
    item, use = selected_use(session, entity, curve)
    install_use(session, item, rebound_use(session, use, mode))


def reverse(session: "Session", entity: str, curve: str, enabled: bool) -> None:
    item, use = selected_use(session, entity, curve)
    install_use(session, item, replace(use, reverse=enabled))


def sampling(session: "Session", entity: str, curve: str, samples: int | None) -> None:
    from .construction_policy import require_topology_edit

    item, use = selected_use(session, entity, curve)
    changed = replace(use, samples=samples)
    if changed != use:
        require_topology_edit(session.document, entity)
        install_use(session, item, changed)


def selected_use(session: "Session", entity: str, curve: str) -> tuple[SCP | Surface, CurveUse]:
    from . import object_operations

    item = session.document.object(entity)
    if isinstance(item, SCP):
        session.editable(entity)
    else:
        object_operations.editable(session, entity)
    use = next((u for u in uses(item) if u.curve == curve), None)
    if not isinstance(item, (SCP, Surface)) or use is None:
        raise ValueError("Consumer does not reference this curve.")
    return item, use


def install_use(session: "Session", item: SCP | Surface, changed: CurveUse) -> None:
    sources = tuple(changed if u.curve == changed.curve else u for u in uses(item))
    install(session, with_uses(item, sources))


def install(session: "Session", item: SCP | Surface) -> None:
    from . import object_operations

    if isinstance(item, Surface):
        object_operations.install(session, item)
    else:
        session.replace_entities({item.id: item})
        construction_tasks.edited(session, {item.id})


def revised[T: SCP | Surface](before: T, after: T) -> T:
    from . import entity_revisions, object_revisions

    if after == before:
        return before
    policy = entity_revisions if isinstance(before, SCP) else object_revisions
    return cast(T, policy.authored(before, after))


def rebound_use(session: "Session", use: CurveUse, mode: str) -> CurveUse:
    local = curve_sources.use_frame(session.engine, session.document, use)
    reference = curve_sources.world(session.engine, session.document, use.reference_frame)
    absolute = curve_sources.world(session.engine, session.document, use.curve)
    bound = matrix(session.engine, reference, absolute, relative=True)
    return replace(use, mode=mode, matrix=local, bind_matrix=bound)
