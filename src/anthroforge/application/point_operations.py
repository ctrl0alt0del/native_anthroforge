"""Construction points and independently captured anatomical Anchors."""

from dataclasses import replace
from typing import Any

from anthroforge.core.points import Anchor, Point

from . import anchor_capture, object_creation, object_operations
from .operations import require_name


def create(session: Any, name: str = "Point", position: Any = None, **placement: Any) -> str:
    state = object_creation.placement(
        session, placement.get("parent", ""), placement.get("owner", ""), placement.get("values")
    )
    item = Point(
        name=require_name(name), position=tuple(position or session.workspace.cursor), **state
    )
    session.replace_document(objects=(*session.document.objects, item))
    return item.id


def point(session: Any, target: str) -> Point:
    item = object_operations.editable(session, target)
    if not isinstance(item, Point):
        raise ValueError("This operation requires a construction Point or Anchor.")
    return item


def update(session: Any, target: str, position: Any) -> None:
    item = point(session, target)
    if isinstance(item, Anchor):
        raise ValueError(
            "Move an Anchor through explicit rebind; its anatomical binding is retained otherwise."
        )
    object_operations.install(session, replace(item, position=tuple(position)))


def anchor(
    session: Any, source: str, parent: str = "", role: str = "", name: str = "Anchor"
) -> dict[str, str]:
    item = point(session, source)
    return anchor_capture.create(session, item, parent, role, require_name(name))


def rebind(session: Any, target: str, parent: str, role: str = "", position: Any = None) -> str:
    item = point(session, target)
    if not isinstance(item, Anchor):
        raise ValueError("Only an Anchor can be rebound; convert an ordinary Point explicitly.")
    return anchor_capture.rebind(session, item, parent, role, position)
