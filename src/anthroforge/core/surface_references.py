"""Anatomical targets have explicit surface roles independent of their presentation."""

from dataclasses import dataclass, field

from .entities import Attachment

ROLES = frozenset(("SCP_GEOMETRY", "TISSUE_BASE", "TISSUE_FINAL"))


@dataclass(frozen=True, slots=True, order=True)
class SurfaceReference:
    target: str
    role: str = "SCP_GEOMETRY"

    def __post_init__(self) -> None:
        if not self.target or self.role not in ROLES:
            raise ValueError("An anatomical surface needs an identity and explicit valid role.")


@dataclass(frozen=True, slots=True)
class CapturedSurface:
    reference: SurfaceReference
    material_asset: str

    def __post_init__(self) -> None:
        if not self.material_asset:
            raise ValueError("A captured surface requires owned material geometry.")


@dataclass(frozen=True, slots=True)
class SurfaceBinding:
    reference: SurfaceReference
    attachment: Attachment = field(default_factory=Attachment)
    capture_scope: str = "CURRENT_PARENT"
    material_asset: str = ""

    def __post_init__(self) -> None:
        if self.capture_scope not in ("CURRENT_PARENT", "ANY_PARENT"):
            raise ValueError("Invalid anatomical capture scope.")
