"""Frozen comparison rows; bulk geometry hashing stays in the native worker."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.object_registry import kind
from anthroforge.core.points import Anchor, Point
from anthroforge.core.results import geometry_asset
from anthroforge.native.comparison import fingerprint
from anthroforge.native.scene import geometry_matrix

from .object_frames import Frames


def rows(context: Any, cancel: int = 0) -> dict[str, Any]:
    frames = Frames(context.engine, context.document)
    return {
        key: row(context, item, frames, cancel)
        for key, item in context.document.registry.records.items()
    }


def row(context: Any, item: Any, frames: Any, cancel: int) -> dict[str, Any]:
    result = getattr(item, "result", None)
    try:
        frame, error = display_frame(context, item, frames), ""
    except ValueError as failure:
        frame, error = [], str(failure)
    return dict(
        id=item.id,
        name=item.name,
        kind=kind(item),
        frame=frame,
        frame_error=error,
        result=asdict(result) if result else None,
        geometry=geometry(context, item, cancel),
    )


def display_frame(context: Any, item: Any, frames: Any) -> list[float]:
    frame = frames.world(item.id)
    offset = getattr(item, "geometry_offset", (0, 0, 0))
    return list(geometry_matrix(context.engine, frame, offset))


def geometry(context: Any, item: Any, cancel: int) -> dict[str, Any]:
    if isinstance(item, Point):
        position = item.resolved_position if isinstance(item, Anchor) else ()
        return dict(kind="POINT", fingerprint=str(position or item.position))
    key = geometry_asset(item)
    if key in context.resources.meshes:
        return mesh_record(context.resources.meshes[key].mesh, cancel)
    if key in context.resources.paths:
        return path_record(context.resources.paths[key].path, cancel)
    return dict(kind="NONE", fingerprint="")


def path_record(path: Any, cancel: int) -> dict[str, Any]:
    return dict(
        kind="PATH",
        fingerprint=fingerprint(path, True, cancel),
        samples=path.count,
        closed=path.closed,
        bounds=list(path.bounds),
    )


def mesh_record(mesh: Any, cancel: int) -> dict[str, Any]:
    return dict(
        kind="MESH",
        fingerprint=fingerprint(mesh, cancel=cancel),
        vertices=mesh.counts[0],
        triangles=mesh.counts[3],
        bounds=list(mesh.bounds),
    )


def compare(before: Any, after: Any, cancel: int = 0) -> dict[str, Any]:
    old, new = rows(before, cancel), rows(after, cancel)
    changes = [
        difference(key, old.get(key), new.get(key)) for key in sorted(old.keys() | new.keys())
    ]
    return dict(
        before_revision=before.document.revision,
        after_revision=after.document.revision,
        rows=changes,
        changed=sum(bool(r["changes"]) for r in changes),
        method="Exact stored coordinates; oriented triangles sorted; FNV pair v1",
        correspondence="No vertex correspondence or displacement inferred",
    )


def difference(key: str, before: Any, after: Any) -> dict[str, Any]:
    changes = []
    if before is None or after is None:
        changes.append("added" if before is None else "removed")
    else:
        if before["frame"] != after["frame"]:
            changes.append("moved")
        if before["geometry"]["fingerprint"] != after["geometry"]["fingerprint"]:
            changes.append("geometry")
    return dict(id=key, name=(after or before)["name"], changes=changes, before=before, after=after)
