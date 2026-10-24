"""Workspace changes do not create anatomical undo steps."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.entities import Workspace
from anthroforge.core.presentation import PRESETS

from . import workspace_policy as policy

if TYPE_CHECKING:
    from .session import Session


def create_workspace(
    session: "Session", name: str, members: list[str], children: bool = False
) -> int:
    policy.available(session)
    ids = policy.members(session.document, members, children)
    workspace = replace(session.workspace, name=name.strip(), members=ids, focused=True)
    session.replace_document(workspaces=(*session.document.workspaces, workspace))
    select_workspace(session, len(session.document.workspaces) - 1)
    return session.active_workspace


def select_workspace(session: "Session", index: int) -> None:
    policy.available(session)
    if not 0 <= index < len(session.document.workspaces):
        raise ValueError("Unknown workspace.")
    session.active_workspace = index
    reprioritize(session)


def reprioritize(session: "Session") -> None:
    for job in session.scheduler.active_jobs:
        if job.state == "queued" and job.writes:
            job.priority = session.priority(set(job.outputs))


def update_workspace(session: "Session", index: int | None = None, **settings: Any) -> None:
    if session.waiting_save and settings.keys() & {"bookmarks", "measurements"}:
        raise ValueError("Wait until saving finishes before changing inspection annotations.")
    index = session.active_workspace if index is None else index
    if not 0 <= index < len(session.document.workspaces):
        raise ValueError("Unknown workspace.")
    if "members" in settings or "focused" in settings:
        policy.available(session)
    changed = replace(session.document.workspaces[index], **policy.settings(settings))
    policy.validate(session, changed, index)
    if changed == session.document.workspaces[index]:
        return
    install(session, index, changed)


def install(session: "Session", index: int, changed: Workspace) -> None:
    workspaces = list(session.document.workspaces)
    workspaces[index] = changed
    session.replace_document(workspaces=tuple(workspaces))
    if index == session.active_workspace:
        reprioritize(session)


def include_created(session: "Session", ids: set[str]) -> None:
    if session.workspace.focused:
        changed = replace(
            session.workspace, members=tuple(sorted(set(session.workspace.members) | ids))
        )
        install(session, session.active_workspace, changed)


def remove_workspace(session: "Session", index: int) -> None:
    policy.available(session)
    if not 0 < index < len(session.document.workspaces):
        raise ValueError("Only named workspaces can be removed.")
    values = tuple(w for i, w in enumerate(session.document.workspaces) if i != index)
    selected = 0 if index == session.active_workspace else session.active_workspace
    session.active_workspace = selected - (index < selected)
    session.replace_document(workspaces=values)
    select_workspace(session, session.active_workspace)


def preset(session: "Session", name: str) -> None:
    if name not in PRESETS:
        raise ValueError("Unknown presentation preset.")
    hidden, unpickable = PRESETS[name]
    update_workspace(session, hidden_categories=hidden, unpickable_categories=unpickable)


def hide(session: "Session", targets: list[str], hidden: bool = True) -> None:
    live = session.document.registry.records.keys() | session.document.mirrors.instances.keys()
    if set(targets) - live:
        raise ValueError("Presentation requires existing source or instance identities.")
    values = set(session.workspace.hidden)
    values = values | set(targets) if hidden else values - set(targets)
    update_workspace(session, hidden=sorted(values))


def isolate(session: "Session", targets: list[str]) -> None:
    live = session.document.registry.records.keys() | session.document.mirrors.instances.keys()
    if not targets or set(targets) - live:
        raise ValueError("Choose existing sources or instances to isolate.")
    update_workspace(session, hidden=sorted(live - set(targets)), mirror_display="BOTH")
