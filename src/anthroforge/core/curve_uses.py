"""Consumer-owned path sampling and placement, independent of authored curves."""

from dataclasses import dataclass

from .construction import integer, validate_range
from .entities import IDENTITY, validate_matrix


@dataclass(frozen=True, slots=True)
class CurveUse:
    curve: str
    reverse: bool = False
    start: float | None = None
    span: float | None = None
    samples: int = 32
    mode: str = "SHAPE_AND_TRANSFORM"
    matrix: tuple[float, ...] = IDENTITY
    bind_matrix: tuple[float, ...] = IDENTITY

    def __post_init__(self) -> None:
        if not self.curve or self.mode not in ("SHAPE_AND_TRANSFORM", "SHAPE_ONLY"):
            raise ValueError("Curve use needs a source and valid transform mode.")
        if not integer(self.samples, 2, 4096):
            raise ValueError("Curve-use sampling must be between 2 and 4096.")
        validate_range(self.start, self.span)
        validate_matrix(self.matrix)
        validate_matrix(self.bind_matrix)
