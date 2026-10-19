"""Tissue-owned material fields and source/target region goals."""

from dataclasses import dataclass, field
from uuid import uuid4

from .surface_references import SurfaceReference
from .tissue_settings import finite_range


@dataclass(frozen=True, slots=True)
class TissueField:
    name: str
    values: tuple[float, ...] = ()
    topology: str = ""
    domain: str = "BASE"

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Tissue field needs a name.")
        if self.domain not in ("BASE", "REST"):
            raise ValueError("Tissue field domain must be Base or Rest.")
        for value in self.values:
            finite_range(value, 0, 1, "Field weight")


@dataclass(frozen=True, slots=True)
class TissueConstraint:
    id: str = field(default_factory=lambda: str(uuid4()))
    mode: str = "FIXED"
    mask: str = "BACKING"
    strength: float = 1.0
    feather: float = 0.0
    offset: float = 0.0
    reference: SurfaceReference | None = None
    bindings: tuple[tuple[float, ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.id or not self.mask or self.mode not in ("FIXED", "SOFT"):
            raise ValueError("A tissue constraint needs identity, mask and Fixed/Soft mode.")
        finite_range(self.strength, 0, 1, "Constraint strength")
        finite_range(self.feather, 0, 1, "Constraint feather")
        finite_range(self.offset, -1000, 1000, "Constraint offset")
