"""Explicit engine conversion choices; evaluated samples never imply routing constraints."""

from dataclasses import dataclass

from .construction_values import integer
from .curve_engines import PathSettings, RoutingSettings


@dataclass(frozen=True, slots=True)
class ConversionSpec:
    curve: str
    settings: PathSettings
    mode: str = "EVALUATED"
    samples: int = 64
    points: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.mode not in ("AUTHORED", "EVALUATED") or not integer(self.samples, 3, 4096):
            raise ValueError("Choose authored points or 3–4096 evaluated samples.")
        if isinstance(self.settings, RoutingSettings) and (
            self.mode != "AUTHORED" or not self.points
        ):
            raise ValueError("Routing conversion requires explicitly selected authored points.")
        if len(set(self.points)) != len(self.points):
            raise ValueError("Routing point selection must be unique.")
