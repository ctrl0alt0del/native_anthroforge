"""Immutable painting inputs; effects and persisted fields belong to consumers."""

from dataclasses import dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class Brush:
    radius: float = 40
    weight: float = 1
    strength: float = 1
    falloff: float = 1
    through: bool = False
    space: str = "SCREEN"

    def native(self) -> tuple[float, ...]:
        return self.radius, self.weight, self.strength, self.falloff, float(self.through)


def brush(value: Any = None) -> Brush:
    result = Brush(**value) if isinstance(value, dict) else Brush(*(value or ()))
    ranges = ((1, 4096), (0, 1), (0, 1), (0.05, 20))
    if result.space != "SCREEN" or not isinstance(result.through, (bool, int)):
        raise ValueError("Only screen-space brushes and boolean Paint Through are supported.")
    for number, (low, high) in zip(result.native()[:4], ranges, strict=True):
        if not isfinite(number) or not low <= number <= high:
            raise ValueError("Brush radius, weight, strength or falloff is outside its range.")
    return result


def samples(values: Any) -> tuple[tuple[float, float], ...]:
    result = tuple(tuple(float(x) for x in row) for row in values)
    if len(result) > 4096 or any(len(row) != 2 for row in result):
        raise ValueError("A stroke requires at most 4,096 two-dimensional samples.")
    if any(not isfinite(x) for row in result for x in row):
        raise ValueError("Paint samples must be finite.")
    return result  # type: ignore[return-value]


@dataclass(frozen=True)
class StrokeInput:
    brush: Brush
    view: tuple[float, ...]
    samples: tuple[tuple[float, float], ...] = ()


@dataclass(frozen=True)
class SurfaceReference:
    target: str
    stage: str
    asset: str
    context: str


@dataclass(frozen=True)
class Provenance:
    document: str
    revision: int
    surface: SurfaceReference
