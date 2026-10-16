"""Explicit editing operations, independent of viewport selection."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.entities import SCP, Attachment, descendants

from . import evaluation

if TYPE_CHECKING:
    from .session import Session


def require_name(name: str) -> str:
    if not name.strip():
        raise ValueError("Name must not be empty.")
    return name.strip()


def parent_for(session: "Session", parent: str) -> str:
    if not session.document.entities:
        if parent:
            raise ValueError("An empty document has no parent SCP.")
        return ""
    if not parent:
        raise ValueError("Choose a parent SCP in this document.")
    session.editable(parent)
    return parent


def empty(session: "Session", name: str, parent: str = "") -> str:
    parent = parent_for(session, parent)
    entity = SCP(
        require_name(name),
        parent=parent,
        attachment=Attachment(parent_mode="OBJECT_ORIGIN", child_mode="OBJECT_ORIGIN"),
    )
    session.replace_document(entities=(*session.document.entities, entity))
    if parent:
        evaluation.request(session, {entity.id}, {entity.id})
    return entity.id


def rename(session: "Session", entity: str, name: str) -> None:
    item = session.editable(entity)
    session.replace_entities({entity: replace(item, name=require_name(name))}, authored=False)


def delete(session: "Session", entity: str) -> None:
    session.editable(entity)
    removed = descendants(session.document.entities, entity)
    for entity_id in removed:
        session.editable(entity_id)
    session.scheduler.invalidate(removed)
    session.replace_document(
        entities=tuple(e for e in session.document.entities if e.id not in removed)
    )


def duplicate(session: "Session", entity: str, parent: str = "") -> str:
    source = session.editable(entity)
    parent = parent_for(session, parent or source.parent or source.id)
    ids = descendants(session.document.entities, entity)
    mapping = {key: str(uuid4()) for key in ids}
    copies = [copied(item, mapping, parent) for item in session.document.entities if item.id in ids]
    session.replace_document(entities=(*session.document.entities, *copies))
    evaluation.request(session, set(mapping.values()), {mapping[entity]})
    return mapping[entity]


def copied(item: SCP, mapping: dict[str, str], parent: str) -> SCP:
    return replace(
        item,
        id=mapping[item.id],
        parent=mapping.get(item.parent, parent),
        name=item.name + " copy",
        generation=0,
    )


def reparent(session: "Session", entity: str, parent: str) -> None:
    item = session.editable(entity)
    if not item.parent:
        raise ValueError("The root cannot be reparented; wrap it in an empty root instead.")
    parent_for(session, parent)
    if parent in descendants(session.document.entities, entity):
        raise ValueError("Reparenting would create a cycle.")
    settings = origin_if_empty(session, parent, item.attachment)
    session.replace_entities({entity: replace(item, parent=parent, attachment=settings)})
    evaluation.request(session, descendants(session.document.entities, entity), {entity})


def origin_if_empty(session: "Session", parent: str, settings: Attachment) -> Attachment:
    return (
        settings
        if session.document.entity(parent).asset
        else replace(settings, parent_mode="OBJECT_ORIGIN")
    )


def wrap_root(session: "Session", name: str = "Assembly") -> str:
    if not session.document.entities:
        return empty(session, name)
    root = next(item for item in session.document.entities if not item.parent)
    session.editable(root.id)
    group = make_group(name)
    changed = replace(
        root, parent=group.id, attachment=replace(root.attachment, parent_mode="OBJECT_ORIGIN")
    )
    entities = tuple(changed if item.id == root.id else item for item in session.document.entities)
    session.replace_document(entities=(group, *entities))
    evaluation.request(session, {root.id}, {root.id})
    return group.id


def make_group(name: str) -> SCP:
    settings = Attachment(parent_mode="OBJECT_ORIGIN", child_mode="OBJECT_ORIGIN")
    return SCP(require_name(name), attachment=settings)


def transform(session: "Session", entity: str, values: list[float]) -> None:
    item = session.editable(entity)
    changed = remember_parent(session, replace(item, matrix=session.engine.transform(values)))
    session.replace_entities({entity: changed})
    schedule_edit(session, entity)


def schedule_edit(session: "Session", entity: str) -> None:
    item = session.document.entity(entity)
    affected = descendants(session.document.entities, entity)
    session.scheduler.invalidate(affected)
    mode = session.document.update_mode if item.update_mode == "INHERIT" else item.update_mode
    mark_edited(session, entity, affected)
    if mode == "LIVE" and session.document.attachments_enabled:
        evaluation.request(session, affected, {entity})


def mark_edited(session: "Session", entity: str, affected: set[str]) -> None:
    changed = {key: mark_entity(session.document.entity(key), key == entity) for key in affected}
    session.replace_entities(changed, authored=False)


def remember_parent(session: "Session", item: SCP) -> SCP:
    if not item.parent:
        return item
    parent = session.document.entity(item.parent)
    return replace(
        item, capture_parent_matrix=parent.matrix, capture_parent_offset=parent.geometry_offset
    )


def mark_entity(item: SCP, directly_edited: bool) -> SCP:
    status = "edited" if directly_edited or item.status == "edited" else "stale"
    return replace(item, status=status)


def released(session: "Session") -> None:
    roots = {
        e.id
        for e in session.document.entities
        if e.status == "edited"
        and (e.update_mode if e.update_mode != "INHERIT" else session.document.update_mode)
        == "ON_RELEASE"
    }
    targets = set().union(*(descendants(session.document.entities, root) for root in roots))
    if targets and session.document.attachments_enabled:
        evaluation.request(
            session, targets, {e.id for e in session.document.entities if e.status == "edited"}
        )


def attachment(session: "Session", entity: str, **options: Any) -> None:
    item = session.editable(entity)
    settings = replace(item.attachment, **options)
    validate_attachment(settings)
    if not item.parent:
        raise ValueError("The root has no parent attachment.")
    if settings.parent_mode == "SURFACE_NEAREST" and not session.document.entity(item.parent).asset:
        raise ValueError("Parent has no surface; choose Object Origin.")
    if settings.child_mode != "OBJECT_ORIGIN" and not item.asset:
        raise ValueError("Child has no geometry; choose Object Origin.")
    changed = remember_parent(session, replace(item, attachment=settings, status="edited"))
    session.replace_entities({entity: changed})
    evaluation.request(session, descendants(session.document.entities, entity), {entity})


def validate_attachment(settings: Attachment) -> None:
    if settings.parent_mode not in ("SURFACE_NEAREST", "OBJECT_ORIGIN"):
        raise ValueError("Invalid parent anchor mode.")
    if settings.child_mode not in ("FACE_CENTER", "VERTEX_NEAREST", "OBJECT_ORIGIN"):
        raise ValueError("Invalid child anchor mode.")
    if settings.strategy not in ("AUTO", "STABLE_SURFACE", "DEFORMATION_FLOW"):
        raise ValueError("Invalid rotation strategy.")
    if settings.face_lock < -1 or settings.vertex_lock < -1:
        raise ValueError("Anchor lock must be -1 or a valid element index.")


def recapture(session: "Session", entity: str) -> str:
    item = session.editable(entity)
    session.replace_entities({entity: remember_parent(session, replace(item, status="edited"))})
    return evaluation.request(session, descendants(session.document.entities, entity), {entity})


def move_origin(session: "Session", entity: str) -> None:
    from anthroforge.native.attachments import move_origin as native_origin

    item = native_origin(session.engine, session.editable(entity))
    session.replace_entities({entity: item})
    targets = descendants(session.document.entities, entity)
    evaluation.request(session, targets, targets)


def toggle_attachments(session: "Session", enabled: bool) -> None:
    ids = {e.id for e in session.document.entities}
    session.scheduler.invalidate(ids)
    session.replace_document(attachments_enabled=bool(enabled))
    if enabled:
        evaluation.request(session, ids, ids)


def update_mode(session: "Session", mode: str, entity: str = "") -> None:
    if mode not in ("LIVE", "ON_RELEASE", "MANUAL", "INHERIT"):
        raise ValueError("Invalid update mode.")
    if entity:
        item = session.editable(entity)
        session.replace_entities({entity: replace(item, update_mode=mode)})
    else:
        session.replace_document(update_mode=mode)


def color(session: "Session", entity: str, value: str) -> None:
    import re

    if re.fullmatch(r"#[0-9a-fA-F]{6}", value) is None:
        raise ValueError("Color must be a six-digit hexadecimal RGB value.")
    item = session.editable(entity)
    session.replace_entities({entity: replace(item, color=value)}, authored=False)
