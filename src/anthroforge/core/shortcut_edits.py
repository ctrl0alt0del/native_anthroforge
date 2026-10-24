"""Pending shortcut edit intent; portable bindings, never native caches or UI gestures."""

from dataclasses import dataclass, field
from uuid import uuid4

from .entities import SCP, Attachment
from .shortcuts import AttachmentPolicy


@dataclass(frozen=True, slots=True)
class OverrideBinding:
    """Effective edit binding: retained authored attachment or a temporary override."""

    target: str
    attachment: Attachment


@dataclass(frozen=True, slots=True)
class OwnerAnchor:
    mode: str
    index: int
    fallback: tuple[float, ...]
    parent_local: tuple[float, ...]
    material_asset: str = ""
    material_binding: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class ShortcutEdit:
    shortcut: str
    owner: str
    policy: AttachmentPolicy
    targets: tuple[str, ...]
    opening: tuple[SCP, ...]
    id: str = field(default_factory=lambda: str(uuid4()))
    bindings: tuple[OverrideBinding, ...] = ()
    anchor: OwnerAnchor | None = None
    status: str = "pending"
    error: str = ""

    def __post_init__(self) -> None:
        if not self.shortcut or self.status not in ("pending", "ready", "failed"):
            raise ValueError("Invalid pending shortcut edit context.")
        if not self.owner and (self.policy.backsolve or self.policy.descendants):
            raise ValueError("Shortcut attachment overrides require an owning SCP or scope.")
