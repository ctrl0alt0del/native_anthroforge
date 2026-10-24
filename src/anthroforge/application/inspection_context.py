"""Owned read-only inputs allow inspection workers to outlive document edits."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.entities import Workspace
from anthroforge.native.mesh import GeometryEngine

from .assets import Asset
from .resources import Resources

if TYPE_CHECKING:
    from .session import Session


def scene_signature(document: Document) -> tuple[object, ...]:
    """Conservative geometry read set; camera/workspace/name edits are not geometry inputs."""
    return (
        document.id,
        document.entities,
        document.controls,
        document.objects,
        document.junctions,
        document.attachments_enabled,
        document.mirror_rules,
        tuple(document.mirrors.placements.items()),
    )


@dataclass(frozen=True)
class InspectionContext:
    document: Document
    resources: Resources
    engine: GeometryEngine
    workspace: Workspace
    routing_backend: str = "CUSTOM"

    @property
    def assets(self) -> dict[str, Asset]:
        return self.resources.meshes


def freeze(session: "Session") -> InspectionContext:
    resources = session.resources.selected(session.document)
    return InspectionContext(
        session.document,
        resources,
        session.engine,
        session.workspace,
        session.preferences.value.routing_backend,
    )
