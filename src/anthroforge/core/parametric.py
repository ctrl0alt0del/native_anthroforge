"""Engine-owned equations and typed variables; coordinates are evaluated results."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any, Literal
from uuid import uuid4

from .construction_values import integer
from .expressions import Symbol
from .numeric_properties import validate_number


@dataclass(frozen=True, slots=True)
class Variable:
    name: str
    value: int | float = 1.0
    numeric_type: str = "REAL"
    dimension: str = "SCALAR"
    label: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        Symbol(self.name, self.numeric_type, self.dimension)
        validate_number(self.value, self.numeric_type)
        if self.name in ("t", "m", "rad", "pi", "e") or not self.id:
            raise ValueError("Variable name is reserved or its identity is missing.")


@dataclass(frozen=True, slots=True)
class Interval:
    start: float = 0.0
    end: float = 1.0
    start_expression: str = ""
    end_expression: str = ""

    def __post_init__(self) -> None:
        if not isfinite(self.start) or not isfinite(self.end):
            raise ValueError("Parameter interval must be finite.")
        require_expressions((self.start_expression, self.end_expression))


@dataclass(frozen=True, slots=True)
class ParametricSettings:
    x: str = "t*m"
    y: str = "0*m"
    z: str = "0*m"
    interval: Interval = field(default_factory=Interval)
    resolution: int = 64
    variables: tuple[Variable, ...] = ()
    interpolation: str = "POLYLINE"
    bezier_resolution: int = 24
    kind: Literal["PARAMETRIC"] = field(default="PARAMETRIC", init=False)

    def __post_init__(self) -> None:
        require_expressions((self.x, self.y, self.z))
        if self.interpolation not in ("POLYLINE", "BEZIER"):
            raise ValueError("Choose polyline or Bézier Parametric interpolation.")
        if not integer(self.bezier_resolution, 1, 1024):
            raise ValueError("Bézier resolution must be between 1 and 1024.")
        if not integer(self.resolution, 2, 1000000):
            raise ValueError("Parametric resolution must be between 2 and 1000000 points.")
        names, ids = [v.name for v in self.variables], [v.id for v in self.variables]
        if len(names) > 255 or len(set(names)) != len(names) or len(set(ids)) != len(ids):
            raise ValueError("Use at most 255 variables with unique names and identities.")


def require_expressions(values: tuple[str, ...]) -> None:
    if any(not isinstance(v, str) or len(v) > 8192 for v in values):
        raise ValueError("Expressions must be strings with at most 8192 characters.")


def decode(values: dict[str, Any]) -> ParametricSettings:
    data = dict(values)
    data.pop("kind", None)
    data["variables"] = tuple(Variable(**v) for v in data.get("variables", ()))
    data["interval"] = Interval(**data.get("interval", {}))
    return ParametricSettings(**data)
