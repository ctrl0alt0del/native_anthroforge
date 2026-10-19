"""Standalone points and their substitutable anatomically attached specialization."""

from dataclasses import dataclass, field
from math import isfinite

from .objects import ConstructionObject
from .surface_references import SurfaceBinding


@dataclass(frozen=True, slots=True)
class Point(ConstructionObject):
    position: tuple[float, ...] = (0.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        ConstructionObject.__post_init__(self)
        if len(self.position) != 3 or not all(map(isfinite, self.position)):
            raise ValueError("A point needs three finite coordinates.")


@dataclass(frozen=True, slots=True)
class Anchor(Point):
    binding: SurfaceBinding = field(kw_only=True)
    resolved_position: tuple[float, ...] = ()
    resolved_frame: tuple[float, ...] = ()

    def __post_init__(self) -> None:
        Point.__post_init__(self)
        if self.resolved_position and (
            len(self.resolved_position) != 3 or not all(map(isfinite, self.resolved_position))
        ):
            raise ValueError("Resolved anchor position needs three finite coordinates.")
