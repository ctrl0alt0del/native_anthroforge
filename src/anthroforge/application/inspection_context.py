"""Owned read-only inputs allow inspection workers to outlive document edits."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.entities import Workspace
from anthroforge.native.mesh import GeometryEngine

from .assets import Asset

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class InspectionContext:
    document: Document
    assets: dict[str, Asset]
    engine: GeometryEngine
    workspace: Workspace


def freeze(session: "Session") -> InspectionContext:
    from .geometry_ownership import assets_used

    assets = {key: session.assets[key] for key in assets_used(session.document)}
    return InspectionContext(session.document, assets, session.engine, session.workspace)
