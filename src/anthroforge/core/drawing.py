"""Typed stroke fitting options independent of input devices and rendering."""

from dataclasses import dataclass
from math import isfinite, pi


@dataclass(frozen=True, slots=True)
class FitSettings:
    method: str = "REFIT"
    error: float = 0.002
    corner_angle: float = 70 * pi / 180
    closed: bool = False

    def __post_init__(self) -> None:
        if self.method not in ("REFIT", "SPLIT", "POLYLINE"):
            raise ValueError("Unknown stroke fitting method.")
        if not isfinite(self.error) or self.error <= 0:
            raise ValueError("Fitting error must be positive and finite.")
        if not isfinite(self.corner_angle) or not 0 <= self.corner_angle <= pi:
            raise ValueError("Corner angle must be between zero and pi radians.")

    @property
    def method_index(self) -> int:
        return ("REFIT", "SPLIT", "POLYLINE").index(self.method)
