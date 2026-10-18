"""Surfaces reference generic curves; correspondence belongs to the consumer."""

from dataclasses import dataclass
from math import isfinite

from .construction import integer
from .curve_uses import CurveUse
from .objects import ConstructionObject


@dataclass(frozen=True, slots=True)
class SurfaceAlignment:
    point: str = ""
    factor: float = 0.0
    reverse: bool = False

    def __post_init__(self) -> None:
        if not isfinite(self.factor) or not 0 <= self.factor < 1:
            raise ValueError("Surface correspondence requires a finite segment fraction.")


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
