"""Shared construction creation context; association is separate from parenting."""

from typing import TYPE_CHECKING, Any

from anthroforge.core.entities import IDENTITY
from anthroforge.core.objects import ObjectRecord
from anthroforge.core.reference_images import ReferenceImage

if TYPE_CHECKING:
    from .session import Session


def placement(
    session: "Session", parent: str, owner: str, values: list[float] | None
) -> dict[str, Any]:
    if owner:
        session.editable(owner)
    require_parent(session, parent)
    frame = session.engine.transform(values) if values is not None else IDENTITY
    return dict(parent=parent, owners=(owner,) if owner else (), matrix=frame)


def require_parent(session: "Session", parent: str) -> None:
    if parent and isinstance(session.document.object(parent), ReferenceImage):
        raise ValueError("Transform parent cannot be a reference image.")


def validate_parent(session: "Session", item: ObjectRecord) -> None:
    require_parent(session, item.parent)
