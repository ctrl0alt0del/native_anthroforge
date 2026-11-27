"""Skin admission uses resource metadata only, without preparing geometry on the UI thread."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.core.results import geometry_asset
from anthroforge.core.scheduling import Workload


@dataclass(frozen=True)
class SkinWorkload(Workload):
    worker_threads: int = 0


def native_threads(workload: Workload) -> int:
    return workload.worker_threads if isinstance(workload, SkinWorkload) else 4


def counts(resources: Any, document: Any, source: Any) -> tuple[int, int, int]:
    item = document.object(source.owner)
    key = item.final_result.asset if source.kind == "TISSUE" else geometry_asset(item)
    asset = resources.meshes.get(key)
    return mesh_counts(asset.mesh) if asset else (0, 0, 0)


def mesh_counts(mesh: Any) -> tuple[int, int, int]:
    vertices, faces, corners, triangles, _ = mesh.counts
    return vertices, triangles, vertices * 24 + triangles * 24 + corners * 8 + (faces + 1) * 8


def base_counts(resources: Any, document: Any, sources: Any) -> list[tuple[int, int, int]]:
    keys = [document.object(s.owner).base_result.asset for s in sources if s.kind == "TISSUE"]
    return [mesh_counts(resources.meshes[key].mesh) for key in keys if key in resources.meshes]


def sizes_for(resources: Any, document: Any, sources: Any, builder: str) -> Any:
    sizes = [counts(resources, document, source) for source in sources]
    if builder == "AVBD":
        sizes.extend(base_counts(resources, document, sources))
    envelope = resources.meshes.get(document.skin.envelope.asset)
    if envelope:
        sizes.append(mesh_counts(envelope.mesh))
    return sizes


def estimate(resources: Any, document: Any, builder: str = "") -> Workload:
    from .skin_builder_registry import BUILDERS

    builder = builder or document.skin.draft_settings.backend
    sources = skin_sources.contributors(document)
    sizes = sizes_for(resources, document, sources, builder)
    return SkinWorkload(
        entities=len(sources),
        candidates=sum(row[0] for row in sizes),
        triangles=sum(row[1] for row in sizes),
        bytes=sum(row[2] for row in sizes),
        worker_threads=BUILDERS[builder].worker_threads,
    )
