"""Authored nearest-surface deformation, distinct from anatomical attachment."""

from dataclasses import dataclass
from math import isfinite

from .surface_references import SurfaceReference

MODES = ("ON_SURFACE", "INSIDE", "OUTSIDE", "OUTSIDE_SURFACE")


@dataclass(frozen=True, slots=True)
class Shrinkwrap:
    surface: SurfaceReference
    offset: float = 0.0
    mode: str = "ON_SURFACE"

    def __post_init__(self) -> None:
        if not isinstance(self.surface, SurfaceReference):
            raise ValueError("Shrinkwrap requires an explicit target surface role.")
        if not isfinite(self.offset) or self.mode not in MODES:
            raise ValueError("Invalid nearest-surface Shrinkwrap offset or snap mode.")
