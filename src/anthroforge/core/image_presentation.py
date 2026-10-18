"""Per-workspace image appearance does not modify authored placement or source assets."""

from dataclasses import dataclass
from math import isfinite
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .entities import Workspace


@dataclass(frozen=True, slots=True)
class ImagePresentation:
    target: str
    opacity: float = 0.65
    depth: str = "NORMAL"
    side: str = "BOTH"
    orthographic: bool = True
    perspective: bool = True
    pickable: bool = True

    def __post_init__(self) -> None:
        if not self.target or not isfinite(self.opacity) or not 0 <= self.opacity <= 1:
            raise ValueError("Image appearance requires a target and opacity between zero and one.")
        if self.depth not in ("NORMAL", "FRONT", "BACK"):
            raise ValueError("Image depth must be Normal, Front or Back.")
        if self.side not in ("BOTH", "FRONT", "BACK"):
            raise ValueError("Image side must be Both, Front or Back.")


def settings(workspace: "Workspace", target: str) -> ImagePresentation:
    return next(
        (v for v in workspace.reference_images if v.target == target), ImagePresentation(target)
    )


def decode(data: Any) -> ImagePresentation:
    return data if isinstance(data, ImagePresentation) else ImagePresentation(**data)
