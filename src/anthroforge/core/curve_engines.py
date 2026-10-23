"""Typed authored path configuration, independent of consumers and numerical adapters."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Literal

from .construction_values import integer
from .parametric import ParametricSettings


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
    obstacle_mode: str = "AUTO"
    excluded_obstacles: tuple[str, ...] = ()
    kind: Literal["ROUTED"] = field(default="ROUTED", init=False)

    def __post_init__(self) -> None:
        if not integer(self.samples, 3, 4096) or not integer(self.accepted_steps, 1, 1000):
            raise ValueError("Invalid routing sample or accepted-step budget.")
        if not isfinite(self.radius) or self.radius < 0:
            raise ValueError("Routing clearance radius must be finite and nonnegative.")
        if self.obstacle_mode not in ("AUTO", "MANUAL"):
            raise ValueError("Choose automatic or manual routing obstacles.")
        for values in (self.obstacles, self.excluded_obstacles):
            if len(set(values)) != len(values) or any(not key for key in values):
                raise ValueError("Routing obstacles must be unique object identities.")


type PathSettings = BezierSettings | PolylineSettings | RoutingSettings | ParametricSettings


def decode(kind: str = "BEZIER", values: dict[str, Any] | None = None) -> PathSettings:
    if kind == "PARAMETRIC":
        from .parametric import decode as parametric

        return parametric(values or {})
    constructors = dict(BEZIER=BezierSettings, POLYLINE=PolylineSettings, ROUTED=RoutingSettings)
    if kind not in constructors:
        raise ValueError("Unknown curve path engine.")
    settings = dict(values or {})
    if settings.pop("kind", kind) != kind:
        raise ValueError("Curve engine and settings disagree.")
    settings = routing_fields(settings) if kind == "ROUTED" else settings
    return constructors[kind](**settings)  # type: ignore[no-any-return]


def routing_fields(settings: dict[str, Any]) -> dict[str, Any]:
    if "obstacles" in settings and "obstacle_mode" not in settings:
        settings["obstacle_mode"] = "MANUAL"
    for key in ("obstacles", "excluded_obstacles"):
        if key in settings:
            settings[key] = tuple(settings[key])
    return settings


def fields(data: dict[str, Any]) -> dict[str, Any]:
    """Accept explicit API engine/resolution aliases; persistence stores typed settings."""
    state = dict(data)
    settings = state.pop("engine_settings", {})
    kind = state.pop("engine", settings.get("kind", "BEZIER"))
    if "resolution" in state:
        settings = dict(settings, resolution=state.pop("resolution"))
    state["engine_settings"] = decode(kind, settings)
    if state.get("parametric_definition"):
        state["parametric_definition"] = decode("PARAMETRIC", state["parametric_definition"])
    return state
