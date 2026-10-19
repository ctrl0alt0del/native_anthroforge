"""Structural binding edits reuse current-shape capture and the shared path lifecycle."""

from dataclasses import replace
from typing import Any

from anthroforge.core.fibers import Fiber, FiberBinding

from .curve_edit_operations import selected
from .fiber_operations import requested_surface, validate_targets
from .object_operations import install


def require_fiber(session: Any, curve: str, point: str) -> Fiber:
    item = selected(session, curve)
    if not isinstance(item, Fiber) or point not in {p.id for p in item.points}:
        raise ValueError("Select an authored fiber point.")
    return item


def assign(
    session: Any, curve: str, point: str, target: str, scope: str | None = None, role: str = ""
) -> None:
    item = require_fiber(session, curve, point)
    bindings = {b.point: b for b in item.bindings}
    old = bindings.get(point)
    scope = scope if scope is not None else old.capture_scope if old else "CURRENT_PARENT"
    ref = requested_surface(session, dict(target=target, role=role))
    validate_targets(session, ((point, ref, scope),))
    bindings[point] = FiberBinding(point, target, capture_scope=scope, role=ref.role)
    ordered = tuple(bindings[p.id] for p in item.points if p.id in bindings)
    install(session, replace(item, bindings=ordered))


def remove(session: Any, curve: str, point: str) -> None:
    item = require_fiber(session, curve, point)
    if point not in {b.point for b in item.bindings}:
        raise ValueError("This fiber point has no anatomical binding.")
    if not item.closed and point in (item.points[0].id, item.points[-1].id):
        raise ValueError("An open fiber must retain both endpoint bindings.")
    if item.closed and len(item.bindings) == 1:
        raise ValueError("A closed fiber must retain at least one anatomical binding.")
    install(session, replace(item, bindings=tuple(b for b in item.bindings if b.point != point)))
