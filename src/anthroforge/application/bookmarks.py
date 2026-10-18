"""Named workspace cameras are presentation, independent of anatomical transactions."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.inspection_views import CameraBookmark

from .presentation import update_workspace
from .session import Session


def add(session: Session, name: str) -> str:
    view = session.workspace
    value = CameraBookmark(name.strip(), view.camera, view.orthographic)
    update_workspace(session, bookmarks=(*view.bookmarks, value))
    return value.id


def find(session: Session, bookmark: str) -> CameraBookmark:
    for value in session.workspace.bookmarks:
        if value.id == bookmark:
            return value
    raise ValueError("Unknown camera bookmark.")


def restore(session: Session, bookmark: str) -> dict[str, Any]:
    value = find(session, bookmark)
    update_workspace(session, camera=value.camera, orthographic=value.orthographic)
    return asdict(value)


def rename(session: Session, bookmark: str, name: str) -> None:
    changed = replace(find(session, bookmark), name=name.strip())
    values = tuple(changed if v.id == bookmark else v for v in session.workspace.bookmarks)
    update_workspace(session, bookmarks=values)


def remove(session: Session, bookmark: str) -> None:
    find(session, bookmark)
    update_workspace(
        session, bookmarks=tuple(v for v in session.workspace.bookmarks if v.id != bookmark)
    )


def inspect(session: Session) -> list[dict[str, Any]]:
    return [asdict(value) for value in session.workspace.bookmarks]
