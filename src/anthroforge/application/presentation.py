"""Workspace changes do not create anatomical undo steps."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.entities import Workspace, descendants

if TYPE_CHECKING:
    from .session import Session


def create_workspace(
    session: "Session", name: str, members: list[str], children: bool = False
) -> int:
    ids = set(members)
    for entity_id in members:
        session.document.entity(entity_id)
        if children:
            ids |= descendants(session.document.entities, entity_id)
    if not name.strip() or not ids:
        raise ValueError("A focused workspace needs a name and at least one SCP.")
    workspace = Workspace(name=name.strip(), members=tuple(sorted(ids)), focused=True)
    session.replace_document(workspaces=(*session.document.workspaces, workspace))
    session.active_workspace = len(session.document.workspaces) - 1
    return session.active_workspace


def select_workspace(session: "Session", index: int) -> None:
    if not 0 <= index < len(session.document.workspaces):
        raise ValueError("Unknown workspace.")
    session.active_workspace = index
    for job in session.scheduler.jobs:
        if job.state == "queued":
            job.priority = session.priority(set(job.outputs))


def update_workspace(session: "Session", **settings: Any) -> None:
    for key in ("members", "hidden", "unpickable", "camera"):
        if key in settings:
            settings[key] = tuple(settings[key])
    changed = replace(session.workspace, **settings)
    if changed == session.workspace:
        return
    workspaces = list(session.document.workspaces)
    workspaces[session.active_workspace] = changed
    session.replace_document(workspaces=tuple(workspaces))
