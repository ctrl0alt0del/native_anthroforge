"""Planning reads entity/asset counts only; it never traverses mesh samples."""

from pathlib import Path
from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.scheduling import Workload

if TYPE_CHECKING:
    from .resources import Resources
    from .session import Session


def attachments(
    session: "Session", targets: set[str], captures: set[str], document: Document
) -> Workload:
    costs = capture_costs(session, document, captures)
    return Workload(
        entities=len(document.entities),
        affected=len(targets),
        recaptures=len(costs),
        candidates=sum(c[0] for c in costs),
        triangles=sum(c[1] for c in costs),
    )


def capture_costs(
    session: "Session", document: Document, captures: set[str]
) -> list[tuple[int, int]]:
    lookup = {item.id: item for item in document.entities}
    return [
        capture_cost(session, item, lookup[item.parent])
        for item in document.entities
        if item.id in captures and item.parent
    ]


def capture_cost(session: "Session", child: SCP, parent: SCP) -> tuple[int, int]:
    settings = child.attachment
    counts = session.assets[child.asset].mesh.counts if child.asset else (0, 0, 0, 0, 0)
    if settings.child_mode == "OBJECT_ORIGIN":
        candidates = 1
    elif settings.child_mode == "VERTEX_NEAREST":
        candidates = 1 if settings.vertex_lock >= 0 else counts[0]
    else:
        candidates = 1 if settings.face_lock >= 0 else counts[1]
    triangles = 0
    if settings.parent_mode == "SURFACE_NEAREST" and parent.asset:
        triangles = session.assets[parent.asset].mesh.counts[3]
    return candidates, triangles


def source_file(path: Path, document: Document) -> Workload:
    try:
        return Workload(entities=len(document.entities), bytes=path.stat().st_size)
    except OSError:
        return Workload(entities=len(document.entities))


def project_save(resources: "Resources", document: Document) -> Workload:
    from .resources import referenced

    used = referenced(document)
    sizes = [resources.meshes[key].mesh.counts for key in used["meshes"]]
    size = sum(
        vertices * 24 + corners * 8 + (faces + 1) * 8 for vertices, faces, corners, _, _ in sizes
    )
    size += sum(resources.paths[key].path.bytes for key in used["paths"])
    size += sum(len(resources.images[key].encoded) for key in used["images"])
    size += sum(resources.attachments[key].field.bytes for key in used["attachments"])
    return Workload(entities=len(document.entities), bytes=size)
