"""Versioned authored state; snapshots share immutable geometry assets."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .construction import Control
from .entities import SCP, Workspace, validate_tree


@dataclass(frozen=True, slots=True)
class Document:
    name: str = "Untitled"
    id: UUID = field(default_factory=uuid4)
    revision: int = 0
    metres_per_unit: float = field(default=1.0, init=False)
    entities: tuple[SCP, ...] = ()
    attachments_enabled: bool = True
    update_mode: str = "LIVE"
    workspaces: tuple[Workspace, ...] = (Workspace(),)
    controls: tuple[Control, ...] = ()

    def __post_init__(self) -> None:
        from .construction_validation import document

        if not self.name.strip():
            raise ValueError("Document name must not be empty.")
        if self.revision < 0:
            raise ValueError("Document revision must not be negative.")
        validate_tree(self.entities)
        document(self)
        if self.update_mode not in ("LIVE", "ON_RELEASE", "MANUAL"):
            raise ValueError("Invalid document update mode.")

    def entity(self, entity_id: str) -> SCP:
        for item in self.entities:
            if item.id == entity_id:
                return item
        raise ValueError(f"Unknown SCP: {entity_id}")

    def control(self, control_id: str) -> Control:
        for item in self.controls:
            if item.id == control_id:
                return item
        raise ValueError(f"Unknown control: {control_id}")
