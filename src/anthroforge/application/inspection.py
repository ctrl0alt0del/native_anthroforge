"""Read-only inspection contract shared by desktop details and snapshot reports."""

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from anthroforge.core.results import geometry_asset

from . import attachment_inspection as attachments
from .construction_policy import topology_dependents
from .dependency_inspection import relationships

if TYPE_CHECKING:
    from .session import Session


def target(session: "Session", entity: str) -> dict[str, Any]:
    document = session.document
    item = document.index.entities.get(entity) or document.index.controls.get(entity)
    if item is None:
        raise ValueError("Unknown inspection target.")
    return dict(
        **identity(session, item),
        attachment=attachments.describe(session, item),
        relationships=relationships(document, entity),
        topology_locks=locks(session, entity),
        geometry=geometry(session, item),
    )


def identity(session: "Session", item: Any) -> dict[str, Any]:
    document = session.document
    return dict(
        id=item.id,
        name=item.name,
        kind="SCP" if item.id in document.index.entities else item.kind,
        document_revision=document.revision,
        generation=item.generation,
        construction_revision=getattr(item, "construction_revision", None),
        pose_revision=getattr(item, "pose_revision", None),
        result=asdict(item.result),
        editable=not session.workspace.focused or item.id in session.workspace.members,
    )


def locks(session: "Session", entity: str) -> list[dict[str, str]]:
    document = session.document
    if entity not in document.index.entities:
        return []
    return [
        dict(
            id=key,
            name=(document.index.entities.get(key) or document.control(key)).name,
            reason="Child SCP"
            if key in document.index.entities
            else "Incoming control surface attachment",
        )
        for key in topology_dependents(document, entity)
    ]


def geometry(session: "Session", item: Any) -> dict[str, Any]:
    key = geometry_asset(item) if item.id in session.document.index.entities else ""
    if not key:
        return dict(available=False)
    mesh = session.assets[key].mesh
    return dict(
        available=True,
        asset=key,
        vertices=int(mesh.counts[0]),
        polygons=int(mesh.counts[1]),
        triangles=int(mesh.counts[3]),
        bounds_local_metres=list(mesh.bounds),
    )


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
        issues=session.command("issues.list", limit=200, include_dismissed=True),
    )


def all_targets(session: "Session") -> list[str]:
    return [*session.document.index.entities, *session.document.index.controls]
