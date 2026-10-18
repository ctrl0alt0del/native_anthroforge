"""Versioned authored state; snapshots share immutable geometry assets."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from . import object_registry
from .construction import Control
from .document_index import DocumentIndex, build
from .entities import SCP, Workspace
from .junctions import Junction


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
    objects: tuple[object_registry.Construction, ...] = ()
    junctions: tuple[Junction, ...] = ()
    _index: DocumentIndex | None = field(default=None, repr=False, compare=False, kw_only=True)
    _registry: object_registry.ObjectRegistry | None = field(
        default=None, repr=False, compare=False, kw_only=True
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Document name must not be empty.")
        if self.revision < 0:
            raise ValueError("Document revision must not be negative.")
        object.__setattr__(self, "_index", build(self, self._index))
        object.__setattr__(self, "_registry", object_registry.build(self, self._registry))
        if self.update_mode not in ("LIVE", "ON_RELEASE", "MANUAL"):
            raise ValueError("Invalid document update mode.")

    def entity(self, entity_id: str) -> SCP:
        if entity_id not in self.index.entities:
            raise ValueError(f"Unknown SCP: {entity_id}")
        return self.index.entities[entity_id]

    def control(self, control_id: str) -> Control:
        if control_id not in self.index.controls:
            raise ValueError(f"Unknown control: {control_id}")
        return self.index.controls[control_id]

    @property
    def registry(self) -> object_registry.ObjectRegistry:
        assert self._registry is not None
        return self._registry

    def object(self, object_id: str) -> object_registry.SceneObject:
        return self.registry.get(object_id)

    @property
    def index(self) -> DocumentIndex:
        assert self._index is not None
        return self._index
