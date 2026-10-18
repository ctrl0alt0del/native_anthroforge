"""One membership/editability policy for all workspace clients."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.entities import Workspace, descendants

if TYPE_CHECKING:
    from .session import Session


TUPLES = {"members", "hidden", "unpickable", "camera", "hidden_categories", "unpickable_categories"}


def settings(values: dict[str, Any]) -> dict[str, Any]:
    return {key: tuple(value) if key in TUPLES else value for key, value in values.items()}


def members(document: Document, values: list[str], children: bool = False) -> tuple[str, ...]:
    selected = set(values)
    live = document.index.entities.keys() | document.index.controls.keys()
    if selected - live:
        raise ValueError("Workspace contains an unknown SCP or control.")
    if children:
        for key in values:
            if key in document.index.entities:
                selected |= descendants(document.entities, key)
    if not selected:
        raise ValueError("A focused workspace needs at least one SCP or control.")
    return tuple(sorted(selected))


def available(session: "Session") -> None:
    if session.waiting_save or session.history.before is not None:
        raise ValueError("Finish the current edit or save before changing workspace membership.")


def validate(session: "Session", workspace: Workspace, index: int) -> None:
    if index == 0 and (workspace.focused or workspace.members):
        raise ValueError("The whole-document workspace cannot restrict membership.")
    if index != 0 and not workspace.focused:
        raise ValueError("Named workspaces must retain explicit membership.")
    validate_references(session, workspace, session.document.workspaces[index])


def validate_references(session: "Session", workspace: Workspace, previous: Workspace) -> None:
    # Retain deleted IDs for undo; validate new references, not historical membership.
    live = session.document.index.entities.keys() | session.document.index.controls.keys()
    for field in ("members", "hidden", "unpickable"):
        added = set(getattr(workspace, field)) - set(getattr(previous, field))
        if added - live:
            raise ValueError("Workspace references an unknown SCP or control.")
