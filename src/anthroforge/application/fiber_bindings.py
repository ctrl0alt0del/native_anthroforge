"""Structural binding edits reuse current-shape capture and the shared path lifecycle."""

from dataclasses import replace
from math import isfinite
from typing import Any

from anthroforge.core.fibers import Fiber, FiberBinding

from . import curve_edit_state
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
    bindings[point] = FiberBinding(
        point, ref.target, capture_scope=scope, role=ref.role, instance=ref.instance
    )
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


def rebind_all(session: Any, curve: str) -> None:
    from .fiber_support_operations import selected

    item = selected(session, curve)
    current = curve_edit_state.current(session, item)
    edit = item.edit or curve_edit_state.baseline(session, item)
    bindings = tuple(replace(b, attachment=None, material_asset="") for b in item.bindings)
    edit = replace(edit, rebind=tuple(b.point for b in bindings), offsets=(), shape=False)
    install(session, replace(current, bindings=bindings, edit=edit))


def normal_offset(session: Any, curve: str, point: str, value: float) -> None:
    item = require_fiber(session, curve, point)
    if not isfinite(value):
        raise ValueError("Normal Offset must be finite.")
    bindings = offset_bindings(item, point, value)
    if bindings == item.bindings:
        return
    edit = item.edit or curve_edit_state.baseline(session, item)
    edit = replace(
        edit,
        shape=True,
        offsets=tuple(sorted(set(edit.offsets) | {point})),
        rebind=tuple(k for k in edit.rebind if k != point),
    )
    install(session, replace(item, bindings=bindings, edit=edit))


def offset_bindings(item: Fiber, point: str, value: float) -> tuple[FiberBinding, ...]:
    if point not in {b.point for b in item.bindings}:
        raise ValueError("Select a bound Fiber point to change Normal Offset.")
    return tuple(offset_binding(b, value) if b.point == point else b for b in item.bindings)


def offset_binding(binding: FiberBinding, value: float) -> FiberBinding:
    if binding.attachment is None:
        raise ValueError("Wait for the anatomical point binding before editing its offset.")
    record = list(binding.attachment.binding)
    record[17] = value
    return replace(binding, attachment=replace(binding.attachment, binding=tuple(record)))
