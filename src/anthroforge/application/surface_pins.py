"""Structural pin identity selection belongs to accepted curve inputs, not a later UI state."""

from typing import Any

from anthroforge.core.fibers import Fiber

from .consumed_paths import accepted


def protected(curve: Any) -> set[str]:
    bound = {b.point for b in curve.bindings} if isinstance(curve, Fiber) else set()
    return bound | {p.id for p in curve.points if p.stacking_fixed or p.protected_crease}


def points(document: Any, resources: Any, order: Any) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for row, key in enumerate(order):
        curve = accepted(document, resources.paths, key).authored
        identities = protected(curve)
        result.extend((row, i) for i, point in enumerate(curve.points) if point.id in identities)
    return result
