"""Anatomical bindings extend the same curve contract consumed by construction."""

from dataclasses import dataclass

from .construction import Curve
from .entities import Attachment


@dataclass(frozen=True, slots=True)
class FiberBinding:
    point: str
    target: str
    attachment: Attachment
    capture_scope: str = "CURRENT_PARENT"

    def __post_init__(self) -> None:
        if not self.point or not self.target or not self.attachment.binding:
            raise ValueError("Fiber binding requires a point, target and captured attachment.")
        if self.capture_scope not in ("CURRENT_PARENT", "ANY_PARENT"):
            raise ValueError("Invalid fiber capture scope.")


@dataclass(frozen=True, slots=True)
class Fiber(Curve):
    bindings: tuple[FiberBinding, ...] = ()
    attachment_asset: str = ""
    supports: tuple[str, ...] = ()

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
