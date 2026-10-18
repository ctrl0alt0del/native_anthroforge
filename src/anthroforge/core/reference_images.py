"""Authored image placement and calibration; textures are separately owned assets."""

from dataclasses import dataclass
from math import isfinite

from .objects import ConstructionObject


@dataclass(frozen=True, slots=True)
class ImageCalibration:
    first: tuple[float, float]
    second: tuple[float, float]
    distance: float

    def __post_init__(self) -> None:
        if len(self.first) != 2 or len(self.second) != 2:
            raise ValueError("Image landmarks use normalized 2D image coordinates.")
        if any(not 0 <= v <= 1 for v in (*self.first, *self.second)):
            raise ValueError("Image landmarks must lie within the image.")
        if not all(isfinite(v) for v in (*self.first, *self.second, self.distance)):
            raise ValueError("Image calibration requires finite values.")
        if self.distance <= 0 or self.first == self.second:
            raise ValueError("Calibration requires positive distance and distinct landmarks.")


@dataclass(frozen=True, slots=True)
class ReferenceImage(ConstructionObject):
    source: str = ""
    width: float = 1.0
    height: float = 1.0
    calibration: ImageCalibration | None = None

    def __post_init__(self) -> None:
        ConstructionObject.__post_init__(self)
        if not self.source:
            raise ValueError("A reference image requires an embedded source asset.")
        if any(not isfinite(v) or v <= 0 for v in (self.width, self.height)):
            raise ValueError("Image physical dimensions must be positive and finite.")
