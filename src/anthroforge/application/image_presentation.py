"""Shared image presentation operations, independent of geometry computation and history."""

from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.image_presentation import settings

from . import image_operations, presentation

if TYPE_CHECKING:
    from .session import Session


def update(session: "Session", target: str, **options: Any) -> None:
    image_operations.selected(session, target)
    changed = replace(settings(session.workspace, target), **options)
    retained = tuple(v for v in session.workspace.reference_images if v.target != target)
    presentation.update_workspace(session, reference_images=(*retained, changed))


def inspect(session: "Session", target: str) -> dict[str, Any]:
    image_operations.selected(session, target)
    return asdict(settings(session.workspace, target))
