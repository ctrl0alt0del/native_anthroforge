"""Read-only inspection contract shared by desktop details and snapshot reports."""

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from anthroforge.core.object_registry import kind
from anthroforge.core.results import geometry_asset

from . import attachment_inspection as attachments
from .dependency_inspection import relationships
from .inspection_context import InspectionContext
from .workspace_policy import included

if TYPE_CHECKING:
    from .session import Session


def target(session: "Session | InspectionContext", entity: str) -> dict[str, Any]:
    document = session.document
    item = document.registry.records.get(entity)
    if item is None:
        raise ValueError("Unknown inspection target.")
    return dict(
        **identity(session, item),
        attachment=attachments.describe(session, item),
        relationships=relationships(document, entity),
        topology_locks=locks(session, entity),
        geometry=geometry(session, item),
    )


def identity(session: "Session | InspectionContext", item: Any) -> dict[str, Any]:
    document = session.document
    return dict(
        id=item.id,
        name=item.name,
        kind=item.kind if item.id in document.index.controls else kind(item),
        document_revision=document.revision,
        generation=item.generation,
        construction_revision=getattr(item, "construction_revision", None),
        pose_revision=getattr(item, "pose_revision", None),
        result=asdict(item.result),
        editable=included(document, session.workspace, item.id),
    )


def locks(session: "Session | InspectionContext", entity: str) -> list[dict[str, str]]:
    from .construction_policy import topology_locks

    return topology_locks(session.document, entity)


def geometry(session: "Session | InspectionContext", item: Any) -> dict[str, Any]:
    from . import construction_inspection

    if item.id in session.document.registry.construction:
        return construction_inspection.geometry(session, item)
    key = geometry_asset(item) if item.id in session.document.index.entities else ""
    if not key:
        return dict(available=False)
    return construction_inspection.mesh_geometry(session.assets[key].mesh, key)


def snapshot(session: "Session", entities: list[str] | None = None) -> dict[str, Any]:
    document = session.document
    selected = entities if entities is not None else all_targets(session)
    return dict(
        schema_version=1,
        document=str(document.id),
        revision=document.revision,
        coordinate_system="right-handed Z-up; canonical metres; row-major affine matrices",
        provisional=session.history.before is not None,
        selected=list(selected),
        workspace=asdict(session.workspace),
        entities=[target(session, key) for key in selected],
        issues=issue_records(session),
    )


def all_targets(session: "Session | InspectionContext") -> list[str]:
    return list(session.document.registry.records)


def issue_records(session: "Session") -> dict[str, Any]:
    session.issues.listening.discover_changes()
    view = session.issues.presentation
    return dict(**view.status(), records=view.filtered({}, "", True))
