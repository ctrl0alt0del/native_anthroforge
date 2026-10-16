"""Accepted control frames for display and safe reference removal after failed evaluation."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Control
from anthroforge.core.entities import Attachment
from anthroforge.core.results import ControlResult
from anthroforge.native.construction import matrix


def stable_frame(session: Any, control: Control) -> tuple[float, ...]:
    from .control_operations import evaluation

    if control.support and control.result.matrix:
        return control.result.matrix
    try:
        return evaluation(session).control_frame(control)
    except ValueError:
        if control.result.matrix:
            return control.result.matrix
        raise


def display_frame(session: Any, control: Control) -> tuple[float, ...]:
    return stable_frame(session, control)


def authored_frame(session: Any, control: Control, world: tuple[float, ...]) -> tuple[float, ...]:
    if control.follow:
        parent = session.document.entity(control.follow).matrix
    elif control.support and any(c.id == control.support for c in session.document.controls):
        parent = stable_frame(session, session.document.control(control.support))
    else:
        return world
    return matrix(session.engine, parent, world, relative=True)


def remember(control: Control, world: tuple[float, ...]) -> Control:
    return replace(control, result=ControlResult(matrix=world))


def detached(session: Any, control: Control) -> Control:
    world = stable_frame(session, control)
    return replace(
        control,
        follow="",
        support="",
        matrix=world,
        attachment=Attachment(),
        generation=control.generation + 1,
        result=ControlResult(matrix=world),
    )


def remove_supports(session: Any, removed: set[str]) -> tuple[Control, ...]:
    return tuple(
        detached(session, c) if c.follow in removed or c.support in removed else c
        for c in session.document.controls
    )


def rebase_followers(session: Any, before: Any, after: Any) -> None:
    from .control_operations import install

    for control in session.document.controls:
        if control.follow == before.id:
            world = matrix(session.engine, before.matrix, control.matrix)
            local = matrix(session.engine, after.matrix, world, relative=True)
            install(session, replace(control, matrix=local))
