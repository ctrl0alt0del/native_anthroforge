"""Typed authored path configuration, independent of consumers and numerical adapters."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Literal

from .construction_values import integer


@dataclass(frozen=True, slots=True)
class BezierSettings:
    resolution: int = 24
    kind: Literal["BEZIER"] = field(default="BEZIER", init=False)

    def __post_init__(self) -> None:
        if not integer(self.resolution, 1, 1024):
            raise ValueError("Bézier resolution must be between 1 and 1024.")


@dataclass(frozen=True, slots=True)
class PolylineSettings:
    kind: Literal["POLYLINE"] = field(default="POLYLINE", init=False)


@dataclass(frozen=True, slots=True)
class RoutingSettings:
    samples: int = 64
    radius: float = 0.002
    accepted_steps: int = 24
    obstacles: tuple[str, ...] = ()
    kind: Literal["ROUTED"] = field(default="ROUTED", init=False)

    def __post_init__(self) -> None:
        if not integer(self.samples, 3, 4096) or not integer(self.accepted_steps, 1, 1000):
            raise ValueError("Invalid routing sample or accepted-step budget.")
        if not isfinite(self.radius) or self.radius < 0:
            raise ValueError("Routing clearance radius must be finite and nonnegative.")
        if len(set(self.obstacles)) != len(self.obstacles) or any(
            not key for key in self.obstacles
        ):
            raise ValueError("Routing obstacles must be unique object identities.")


type PathSettings = BezierSettings | PolylineSettings | RoutingSettings


def decode(kind: str = "BEZIER", values: dict[str, Any] | None = None) -> PathSettings:
    constructors = dict(BEZIER=BezierSettings, POLYLINE=PolylineSettings, ROUTED=RoutingSettings)
    if kind not in constructors:
        raise ValueError("Unknown curve path engine.")
    settings = dict(values or {})
    if settings.pop("kind", kind) != kind:
        raise ValueError("Curve engine and settings disagree.")
    if "obstacles" in settings:
        settings["obstacles"] = tuple(settings["obstacles"])
    return constructors[kind](**settings)  # type: ignore[no-any-return]


def fields(data: dict[str, Any]) -> dict[str, Any]:
    """Accept explicit API engine/resolution aliases; persistence stores typed settings."""
    state = dict(data)
    settings = state.pop("engine_settings", {})
    kind = state.pop("engine", settings.get("kind", "BEZIER"))
    if "resolution" in state:
        settings = dict(settings, resolution=state.pop("resolution"))
    state["engine_settings"] = decode(kind, settings)
    return state
