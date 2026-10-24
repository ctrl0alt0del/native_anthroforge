"""Persistent inspection annotations; frozen witnesses never become anatomy constraints."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any
from uuid import uuid4


def finite_tuple(values: tuple[float, ...], count: int) -> None:
    if len(values) != count or not all(map(isfinite, values)):
        raise ValueError("Invalid inspection coordinates.")


@dataclass(frozen=True, slots=True)
class SurfacePoint:
    entity: str
    asset: str
    triangle: int
    weights: tuple[float, ...]
    position: tuple[float, ...]
    frame: tuple[float, ...]
    revision: int
    role: str = ""
    stage: str = ""

    def __post_init__(self) -> None:
        if self.role not in ("", "SCP_GEOMETRY", "TISSUE_BASE", "TISSUE_FINAL"):
            raise ValueError("Invalid measurement surface role.")
        if self.stage not in ("", "base", "rest", "intrinsic", "final"):
            raise ValueError("Invalid measurement tissue stage.")
        finite_tuple(self.position, 3)
        finite_tuple(self.frame, 16)
        finite_tuple(self.weights, 3)
        if not self.entity or not self.asset or self.triangle < 0 or self.revision < 0:
            raise ValueError("Invalid surface witness identity.")
        if min(self.weights) < -1e-6 or abs(sum(self.weights) - 1) > 1e-6:
            raise ValueError("Invalid surface barycentric weights.")


@dataclass(frozen=True, slots=True)
class Measurement:
    name: str
    start: SurfacePoint
    end: SurfacePoint
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.id:
            raise ValueError("Measurement requires a name and identity.")


@dataclass(frozen=True, slots=True)
class CameraBookmark:
    name: str
    camera: tuple[float, ...]
    orthographic: bool
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        finite_tuple(self.camera, 7)
        if not self.name.strip() or not self.id or self.camera[6] <= 0:
            raise ValueError("Invalid camera bookmark.")


def decode_point(data: dict[str, Any]) -> SurfacePoint:
    data = dict(data)
    for key in ("weights", "position", "frame"):
        data[key] = tuple(data[key])
    return SurfacePoint(**data)


def decode_measurement(data: dict[str, Any]) -> Measurement:
    return Measurement(
        **dict(data, start=decode_point(data["start"]), end=decode_point(data["end"]))
    )


def decode_bookmark(data: dict[str, Any]) -> CameraBookmark:
    return CameraBookmark(**dict(data, camera=tuple(data["camera"])))
