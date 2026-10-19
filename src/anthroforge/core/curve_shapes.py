"""Shape changes preserve mandatory endpoint roles without fabricating surface captures."""

from dataclasses import replace
from typing import Any

from .construction import Curve, CurvePoint
from .fibers import Fiber, FiberBinding


def reshaped(item: Curve, **changes: Any) -> Curve:
    points = changes.get("points", item.points)
    closed = changes.get("closed", item.closed)
    if isinstance(item, Fiber):
        changes["bindings"] = shape_bindings(item, points, closed)
    return replace(item, **changes)


def shape_bindings(
    item: Fiber, points: tuple[CurvePoint, ...], closed: bool
) -> tuple[FiberBinding, ...]:
    live = {p.id for p in points}
    bindings = {b.point: b for b in item.bindings if b.point in live}
    if not closed and not item.closed and len(points) >= 2:
        previous = {b.point: b for b in item.bindings}
        for before, after in ((item.points[0], points[0]), (item.points[-1], points[-1])):
            if after.id not in bindings:
                bindings[after.id] = replace(previous[before.id], point=after.id, attachment=None)
    return tuple(bindings[p.id] for p in points if p.id in bindings)


def binding_shape(item: Fiber) -> tuple[Any, ...]:
    return tuple((b.point, b.reference, b.attachment, b.material_asset) for b in item.bindings)
