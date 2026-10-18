"""Accepted control frames for display and safe reference removal after failed evaluation."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Control
from anthroforge.core.results import ControlResult
from anthroforge.native.construction import matrix


def stable_frame(session: Any, control: Control) -> tuple[float, ...]:
    from .object_frames import Frames

    try:
        return Frames(session.engine, session.document).world(control.id)
    except ValueError:
        if control.result.matrix:
            return control.result.matrix
        raise


def display_frame(session: Any, control: Control) -> tuple[float, ...]:
    return stable_frame(session, control)


def authored_frame(session: Any, control: Control, world: tuple[float, ...]) -> tuple[float, ...]:
    from .object_frames import Frames

    parent = Frames(session.engine, session.document).world(control.follow)
    return matrix(session.engine, parent, world, relative=True)


def remember(control: Control, world: tuple[float, ...]) -> Control:
    return replace(control, result=ControlResult(matrix=world))


def detached(session: Any, control: Control) -> Control:
    world = stable_frame(session, control)
    return replace(
        control,
        follow="",
        matrix=world,
        generation=control.generation + 1,
        result=ControlResult(matrix=world),
    )


def remove_supports(session: Any, removed: set[str]) -> tuple[Control, ...]:
    return tuple(
        replace(
            detached(session, c) if c.follow in removed else c,
            owners=tuple(k for k in c.owners if k not in removed),
        )
        for c in session.document.controls
    )
