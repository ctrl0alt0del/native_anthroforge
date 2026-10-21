"""Anatomy-neutral parameter-driven circular segments with an editable radius profile."""

from dataclasses import dataclass
from math import isfinite

from .construction_values import integer


@dataclass(frozen=True, slots=True)
class Segment:
    length: float = 0.3
    radius: float = 0.05
    bend: float = 0.0
    samples: int = 10
    sides: int = 12

    def __post_init__(self) -> None:
        if not all(map(isfinite, (self.length, self.radius, self.bend))):
            raise ValueError("Segment dimensions and angles must be finite.")
        if self.length < 0 or self.radius < 0 or (self.length > 0 and self.radius == 0):
            raise ValueError("Dimensions are nonnegative; a nonempty segment needs positive radius.")
        if not integer(self.samples, 2, 256) or not integer(self.sides, 3, 128):
            raise ValueError("Segment resolution exceeds supported bounds.")


@dataclass(frozen=True, slots=True)
class SegmentChain:
    segments: tuple[Segment, ...] = (Segment(), Segment(), Segment(), Segment())
    spread: float = 0.0
    bend_mode: str = "ADJACENT"
    profile: tuple[float, ...] = (0.0, 1.0, 0.46, 0.76, 0.94, 0.73, 1.0, 0.85)
    unite: bool = True

    def __post_init__(self) -> None:
        if not 1 <= len(self.segments) <= 32 or not all(
            isinstance(s, Segment) for s in self.segments
        ):
            raise ValueError("A segment chain needs 1–32 typed segments.")
        if not isfinite(self.spread) or self.bend_mode not in ("ADJACENT", "CUMULATIVE"):
            raise ValueError("Invalid segment chain angles or bend composition.")
        if not any(s.length > 0 for s in self.segments):
            raise ValueError("A segment chain needs at least one positive length.")
        validate_profile(self.profile)


def validate_profile(profile: tuple[float, ...]) -> None:
    if len(profile) < 4 or len(profile) % 2 or not all(map(isfinite, profile)):
        raise ValueError("Radius profile requires finite XY pairs.")
    if profile[0] != 0 or profile[-2] != 1 or any(y <= 0 for y in profile[1::2]):
        raise ValueError("Radius profile spans 0–1 with positive scale values.")
    if any(a >= b for a, b in zip(profile[::2], profile[2::2], strict=False)):
        raise ValueError("Radius profile positions must increase.")


def topology(chain: SegmentChain | None) -> tuple[object, ...]:
    if chain is None:
        return ()
    return chain.unite, tuple((s.samples, s.sides, s.length == 0) for s in chain.segments)
