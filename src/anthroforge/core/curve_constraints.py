"""Authored routing constraints that conversion must preserve."""

from .construction import Curve
from .fibers import Fiber


def required_points(curve: Curve) -> dict[str, str]:
    result = {p.id: "Shared junction point" for p in curve.points if p.junction}
    if isinstance(curve, Fiber):
        result.update((b.point, "Anatomical binding") for b in curve.bindings)
    if not curve.closed and curve.points:
        for point in (curve.points[0], curve.points[-1]):
            result.setdefault(point.id, "Open endpoint")
    return result
