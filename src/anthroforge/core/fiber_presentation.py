"""Per-workspace Fiber display radius, independent of authored paths and collision clearance."""

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True, slots=True)
class FiberPresentation:
    target: str
    radius: float = 0.001

    def __post_init__(self) -> None:
        if not self.target or not isfinite(self.radius) or self.radius < 0:
            raise ValueError("Fiber appearance requires a target and nonnegative finite radius.")


def settings(workspace: Any, target: str) -> FiberPresentation:
    return next((v for v in workspace.fibers if v.target == target), FiberPresentation(target))


def decode(data: Any) -> FiberPresentation:
    return data if isinstance(data, FiberPresentation) else FiberPresentation(**data)
