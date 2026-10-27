"""Skin admission uses resource metadata only, without preparing geometry on the UI thread."""

from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.results import geometry_asset
from anthroforge.core.scheduling import Workload


def counts(resources: Any, document: Any, source: Any) -> tuple[int, int, int]:
    item = document.object(source.owner)
    key = item.final_result.asset if source.kind == "TISSUE" else geometry_asset(item)
    asset = resources.meshes.get(key)
    return mesh_counts(asset.mesh) if asset else (0, 0, 0)


def mesh_counts(mesh: Any) -> tuple[int, int, int]:
    vertices, faces, corners, triangles, _ = mesh.counts
    return vertices, triangles, vertices * 24 + triangles * 24 + corners * 8 + (faces + 1) * 8


def estimate(resources: Any, document: Any) -> Workload:
    sources = skin_sources.contributors(document)
    sizes = [counts(resources, document, source) for source in sources]
    envelope = resources.meshes.get(document.skin.envelope.asset)
    if envelope:
        sizes.append(mesh_counts(envelope.mesh))
    return Workload(
        entities=len(sources),
        candidates=sum(row[0] for row in sizes),
        triangles=sum(row[1] for row in sizes),
        bytes=sum(row[2] for row in sizes),
    )
