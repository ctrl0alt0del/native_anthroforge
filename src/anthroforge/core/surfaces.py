"""Surfaces reference generic curves; correspondence belongs to the consumer."""

from dataclasses import dataclass

from .construction import integer
from .curve_uses import CurveUse
from .objects import ConstructionObject


@dataclass(frozen=True, slots=True)
class Surface(ConstructionObject):
    curves: tuple[CurveUse, ...] = ()
    kind: str = "LOFT"
    strips: int = 1

    def __post_init__(self) -> None:
        ConstructionObject.__post_init__(self)
        if self.kind not in ("LOFT", "PATCH", "BRANCHED"):
            raise ValueError("Unknown surface construction.")
        required = 1 if self.kind == "PATCH" else 2
        if len(self.curves) < required or (self.kind == "PATCH" and len(self.curves) != 1):
            raise ValueError("Surface requires compatible source curves.")
        if len({use.curve for use in self.curves}) != len(self.curves):
            raise ValueError("A surface cannot consume the same curve twice.")
        if not integer(self.strips, 1, 256):
            raise ValueError("Surface strips must be between 1 and 256.")
