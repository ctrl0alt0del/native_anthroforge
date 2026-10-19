"""Anatomical bindings extend the same curve contract consumed by construction."""

from dataclasses import dataclass

from .construction import Curve
from .entities import Attachment
from .surface_references import CapturedSurface, SurfaceReference


@dataclass(frozen=True, slots=True)
class FiberEdit:
    baseline: str
    candidates: tuple[SurfaceReference, ...]
    rebind: tuple[str, ...] = ()
    shape: bool = True


@dataclass(frozen=True, slots=True)
class FiberBinding:
    point: str
    target: str
    attachment: Attachment | None = None
    capture_scope: str = "CURRENT_PARENT"
    role: str = "SCP_GEOMETRY"
    material_asset: str = ""

    def __post_init__(self) -> None:
        SurfaceReference(self.target, self.role)
        if not self.point or not self.target:
            raise ValueError("Fiber binding requires an authored point and anatomical target.")
        if self.attachment is not None and not self.attachment.binding:
            raise ValueError("A captured fiber attachment requires its surface binding.")
        if self.capture_scope not in ("CURRENT_PARENT", "ANY_PARENT"):
            raise ValueError("Invalid fiber capture scope.")

    @property
    def reference(self) -> SurfaceReference:
        return SurfaceReference(self.target, self.role)

    @property
    def capture(self) -> CapturedSurface:
        return CapturedSurface(self.reference, self.material_asset)


@dataclass(frozen=True, slots=True)
class Fiber(Curve):
    bindings: tuple[FiberBinding, ...] = ()
    attachment_asset: str = ""
    supports: tuple[CapturedSurface, ...] = ()
    edit: FiberEdit | None = None

    def __post_init__(self) -> None:
        Curve.__post_init__(self)
        keys = [binding.point for binding in self.bindings]
        if len(keys) != len(set(keys)) or set(keys) - {point.id for point in self.points}:
            raise ValueError("Fiber bindings require unique authored point identities.")
        if self.closed and not keys:
            raise ValueError("A closed fiber requires at least one anatomical binding.")
        endpoints = {self.points[0].id, self.points[-1].id}
        if not self.closed and not endpoints.issubset(keys):
            raise ValueError("An open fiber requires both endpoint bindings.")
