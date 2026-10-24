"""Presentation edits bypass anatomical history and numerical invalidation."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.fiber_presentation import settings
from anthroforge.core.fibers import Fiber

from . import presentation


def inspect(session: Any, target: str) -> dict[str, Any]:
    if not isinstance(session.document.object(target), Fiber):
        raise ValueError("Fiber appearance requires a Fiber.")
    return asdict(settings(session.workspace, target))


def update(session: Any, target: str, radius: float) -> None:
    inspect(session, target)
    changed = replace(settings(session.workspace, target), radius=float(radius))
    retained = tuple(v for v in session.workspace.fibers if v.target != target)
    presentation.update_workspace(session, fibers=(*retained, changed))
