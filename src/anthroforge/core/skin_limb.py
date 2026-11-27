"""Authored limb settings in metres. None selects automatic dimensioning."""

from dataclasses import dataclass
from math import isfinite


def finite(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


@dataclass(frozen=True, slots=True)
class SkinLimb:
    rest_radius: float | None = None
    boundary_radius: float | None = None
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        for radius in (self.rest_radius, self.boundary_radius):
            if radius is not None and (not finite(radius) or radius <= 0):
                raise ValueError("Manual skin radii must be positive finite lengths in metres.")
        if not isinstance(self.offset, (tuple, list)) or len(self.offset) != 3:
            raise ValueError("Limb offset requires three finite lengths in attachment coordinates.")
        if not all(finite(value) for value in self.offset):
            raise ValueError("Limb offset requires three finite lengths in attachment coordinates.")
        object.__setattr__(self, "offset", tuple(self.offset))
