"""Read-only construction resources and relationships without anatomical proxies."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.fibers import Fiber

from .curve_sources import world


def attachment(session: Any, item: Any) -> dict[str, Any]:
    parent = session.document.registry.records.get(item.parent)
    return dict(
        owner_frame=dict(matrix=world(session.engine, session.document, item.id), available=True),
        transform_parent=item.parent,
        transform_parent_name=parent.name if parent else "",
        bindings=[asdict(binding) for binding in item.bindings] if isinstance(item, Fiber) else [],
    )


def geometry(session: Any, item: Any) -> dict[str, Any]:
    asset = item.result.asset
    if asset in session.resources.paths:
        path = session.resources.paths[asset].path
        result = dict(kind="PATH", samples=path.count, bounds_local_metres=list(path.bounds))
        return dict(result, available=True, asset=asset)
    if asset in session.resources.meshes:
        return mesh_geometry(session.resources.meshes[asset].mesh, asset)
    return dict(available=False)


def mesh_geometry(mesh: Any, asset: str) -> dict[str, Any]:
    return dict(
        available=True,
        kind="MESH",
        asset=asset,
        vertices=int(mesh.counts[0]),
        polygons=int(mesh.counts[1]),
        triangles=int(mesh.counts[3]),
        bounds_local_metres=list(mesh.bounds),
    )
