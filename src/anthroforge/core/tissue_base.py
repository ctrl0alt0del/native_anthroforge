"""Accepted source state: frame, path or material surface; never synthetic anatomy."""

from dataclasses import dataclass

from .entities import IDENTITY, validate_matrix


@dataclass(frozen=True, slots=True)
class TissueBaseState:
    kind: str = "NONE"
    frame: tuple[float, ...] = IDENTITY
    parts: tuple[str, ...] = ("main",)

    def __post_init__(self) -> None:
        if self.kind not in ("NONE", "POINT", "CURVE", "SURFACE"):
            raise ValueError("Unsupported accepted tissue base.")
        validate_matrix(self.frame)
