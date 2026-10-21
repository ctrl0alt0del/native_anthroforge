"""Remove one SCP while retaining children, world poses and shared controls."""

from dataclasses import replace
from typing import TYPE_CHECKING

from anthroforge.core.construction import Control
from anthroforge.core.entities import SCP, descendants
from anthroforge.core.results import geometry_asset

from . import evaluation
from .control_frames import remove_supports
from .object_removal import install as install_construction_removal
from .object_removal import retain_frames, retain_objects
from .operations import make_group
from .presentation import include_created
from .session import merge_entity

if TYPE_CHECKING:
    from .session import Session


def delete(session: "Session", entity: str) -> str:
    item = session.editable(entity)
    children = {e.id for e in session.document.entities if e.parent == entity}
    affected = descendants(session.document.entities, entity)
    session.scheduler.invalidate({entity})
    controls = remove_supports(session, {entity})
    parent = replacement_parent(session, item, bool(children))
    install_removal(session, item, parent, controls)
    resume_children(session, affected - {entity}, children)
    return parent.id if parent else ""


def replacement_parent(session: "Session", item: SCP, has_children: bool) -> SCP | None:
    if item.parent:
        return session.document.entity(item.parent)
    return replace(make_group(item.name + " group"), matrix=item.matrix) if has_children else None


def promoted(item: SCP, parent: SCP) -> SCP:
    mode = item.attachment.parent_mode if geometry_asset(parent) else "OBJECT_ORIGIN"
    settings = replace(item.attachment, parent_mode=mode, binding=(), material_asset="")
    return replace(
        item,
        parent=parent.id,
        attachment=settings,
        capture_parent_matrix=(),
        status="edited",
        error="",
    )


def install_removal(
    session: "Session", item: SCP, parent: SCP | None, controls: tuple[Control, ...]
) -> None:
    remaining = promoted_entities(session, item, parent)
    if not item.parent and parent:
        remaining = (parent, *remaining)
    objects = retain_objects(session, item, parent)
    remaining = retain_frames(session, remaining, item.id)
    install_construction_removal(session, entities=remaining, controls=controls, objects=objects)
    if not item.parent and parent:
        include_created(session, {parent.id})


def promoted_entities(session: "Session", item: SCP, parent: SCP | None) -> tuple[SCP, ...]:
    changed = {
        e.id: promoted(e, parent)
        for e in session.document.entities
        if e.parent == item.id and parent is not None
    }
    authored = session.authored_entities(changed)
    return tuple(
        merge_entity(e, authored.get(e.id, e)) for e in session.document.entities if e.id != item.id
    )


def resume_children(session: "Session", affected: set[str], children: set[str]) -> None:
    from . import construction_tasks, control_tasks, dependencies

    if not children:
        return
    evaluation.request(session, affected, children)
    seeds = {dependencies.Port(key, "pose") for key in affected}
    control_tasks.edited(session, seeds)
    construction_tasks.edited(session, dependencies.affected(session.document, seeds))
    pending = {e.id for e in session.document.entities if e.result.status == "pending"}
    construction_tasks.schedule(session, pending & affected)
