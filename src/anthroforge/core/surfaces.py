"""Surfaces reference generic curves; correspondence belongs to the consumer."""

from dataclasses import dataclass
from math import isfinite

from .construction import integer
from .curve_uses import CurveUse
from .objects import ConstructionObject
from .surface_branches import SurfaceBranch
from .surface_branches import validate as validate_branches


@dataclass(frozen=True, slots=True)
class SurfaceAlignment:
    point: str = ""
    factor: float = 0.0
    reverse: bool = False
    stations: tuple[tuple[str, float], ...] = ()

    def __post_init__(self) -> None:
        if not isfinite(self.factor) or not 0 <= self.factor < 1:
            raise ValueError("Surface correspondence requires a finite segment fraction.")
        validate_stations(self.stations)


def validate_stations(values: tuple[tuple[str, float], ...]) -> None:
    if not values:
        return
    keys = [key for key, _ in values]
    positions = [value for _, value in values]
    if not 2 <= len(values) <= 4096 or len(set(keys)) != len(keys) or not all(keys):
        raise ValueError("Material correspondence requires distinct curve point identities.")
    if not all(map(isfinite, positions)) or positions[0] != 0:
        raise ValueError("Material stations must be finite and start at zero.")
    if any(a >= b for a, b in zip(positions, positions[1:], strict=False)):
        raise ValueError("Material stations must be strictly increasing.")


@dataclass(frozen=True, slots=True)
class Surface(ConstructionObject):
    curves: tuple[CurveUse, ...] = ()
    kind: str = "LOFT"
    strips: int = 0
    exact: bool = True
    patch_resolution: int = 4
    close_across: bool = False
    flip: bool = False
    alignment: tuple[SurfaceAlignment, ...] = ()
    across: tuple[int, ...] = ()
    main: tuple[str, ...] = ()
    branches: tuple[SurfaceBranch, ...] = ()
    accepted_kind: str = ""
    accepted_parts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ConstructionObject.__post_init__(self)
        if self.kind not in ("LOFT", "PATCH", "BRANCHED"):
            raise ValueError("Unknown surface construction.")
        required = 1 if self.kind == "PATCH" else 2
        if len(self.curves) < required or (self.kind == "PATCH" and len(self.curves) != 1):
            raise ValueError("Surface requires compatible source curves.")
        if len({use.curve for use in self.curves}) != len(self.curves):
            raise ValueError("A surface cannot consume the same curve twice.")
        validate_layout(self)
        validate_branches(self)


def validate_layout(item: Surface) -> None:
    if not integer(item.strips, 0, 256) or not integer(item.patch_resolution, 1, 64):
        raise ValueError("Surface strips must be 0..256 and patch resolution 1..64.")
    if item.alignment and len(item.alignment) != len(item.curves):
        raise ValueError("Surface correspondence requires one record per source.")
    if item.across and (
        len(item.across) != len(item.curves) - 1
        or any(not integer(n, 0, 262144) for n in item.across)
    ):
        raise ValueError("Surface density requires one bounded count per adjacent source pair.")
