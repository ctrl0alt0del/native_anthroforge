"""Source-linked spatial identities; reflection never owns authored geometry."""

from dataclasses import dataclass
from math import isfinite

from .entities import IDENTITY

PREFIX = "mirror/"


@dataclass(frozen=True, slots=True)
class MirrorRule:
    target: str
    enabled: bool = False
    inherit: bool = True
    axis: str = "X"
    shift: float = 0.0
    override: bool = False

    def __post_init__(self) -> None:
        if not self.target or self.axis not in ("X", "Y", "Z") or not isfinite(self.shift):
            raise ValueError("Mirror rules require a target, X/Y/Z axis and finite shift.")
        if any(type(v) is not bool for v in (self.enabled, self.inherit, self.override)):
            raise ValueError("Mirror participation settings must be Boolean.")

    @property
    def frame(self) -> tuple[float, ...]:
        values = list(IDENTITY)
        axis = ("X", "Y", "Z").index(self.axis)
        values[axis * 5], values[axis * 4 + 3] = -1.0, 2.0 * self.shift
        return tuple(values)


@dataclass(frozen=True, slots=True, order=True)
class MirrorInstance:
    source: str
    rule: str

    @property
    def id(self) -> str:
        return f"{PREFIX}{self.rule}/{self.source}"


@dataclass(frozen=True, slots=True)
class SharedMirrorTarget:
    source: str
    binding: str


def parse(value: str) -> MirrorInstance | None:
    if not value.startswith(PREFIX):
        return None
    parts = value.split("/")
    if len(parts) != 3 or not all(parts[1:]):
        raise ValueError("Invalid mirrored instance identity.")
    return MirrorInstance(parts[2], parts[1])


def require_source(value: str) -> None:
    if parse(value) is not None:
        raise ValueError("Mirrored instances are read-only; select their source to edit.")


def source(value: str) -> str:
    instance = parse(value)
    return instance.source if instance else value
