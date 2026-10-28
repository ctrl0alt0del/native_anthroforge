"""Settings for one sampled scalar shortcut; fitted bone counts are budgets, not guarantees."""

from dataclasses import dataclass
from math import isfinite

from .skin import choice, integer


@dataclass(frozen=True, slots=True)
class Settings:
    minimum: float
    maximum: float
    bones: int = 4
    samples: int = 9
    strategy: str = "SCALE_AWARE"
    smoothing: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.minimum) or not isfinite(self.maximum) or self.minimum >= self.maximum:
            raise ValueError("Fitting requires a finite increasing shortcut range.")
        integer("fitted bones", self.bones, 1, 64)
        integer("fitting samples", self.samples, 5, 33)
        if self.samples % 2 != 1:
            raise ValueError("Use an odd number of samples to fit both endpoints.")
        choice("fitting strategy", self.strategy, ("SCALE_AWARE", "SINGLE_ACTIVE"))
        if not isfinite(self.smoothing) or self.smoothing < 0:
            raise ValueError("Fitting smoothing must be finite and nonnegative.")
