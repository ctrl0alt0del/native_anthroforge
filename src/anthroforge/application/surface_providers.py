"""Role-aware accepted anatomy surfaces, with an owned mesh lease and exact provenance."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.entities import SCP
from anthroforge.core.results import EvaluationResult, Port, geometry_asset
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native.scene import entity_frame

from .assets import Asset
from .object_frames import Frames


@dataclass(frozen=True)
class SurfaceProvider:
    reference: SurfaceReference
    resource: Asset
    frame: tuple[float, ...]
    result: EvaluationResult
    port: Port
    asset_id: str


def references(document: Any) -> tuple[SurfaceReference, ...]:
    return tuple(
        SurfaceReference(item.id, role)
        for item in document.registry.anatomy.values()
        for role in anatomical_surfaces.roles(item, document.registry.records)
    )


def normalize(document: Any, target: str | SurfaceReference) -> SurfaceReference:
    if isinstance(target, SurfaceReference):
        return anatomical_surfaces.reference(target.target, document.registry.records, target.role)
    return anatomical_surfaces.reference(target, document.registry.records)


def snapshot(
    engine: Any, document: Any, meshes: Any, target: str | SurfaceReference
) -> SurfaceProvider:
    ref = normalize(document, target)
    item = document.object(ref.target)
    result = anatomical_surfaces.result(item, ref.role)
    key = geometry_asset(item) if isinstance(item, SCP) else result.asset
    require_ready(ref, result, key, meshes)
    frame = (
        entity_frame(engine, item)
        if isinstance(item, SCP)
        else Frames(engine, document).world(item.id)
    )
    return SurfaceProvider(ref, meshes[key], frame, result, anatomical_surfaces.port(ref), key)


def require_ready(ref: SurfaceReference, result: EvaluationResult, key: str, meshes: Any) -> None:
    if result.error or result.status in ("failed", "invalid", "cancelled"):
        raise ValueError(f"{ref.role} on {ref.target} failed: {result.error or result.status}")
    if not key or key not in meshes:
        raise ValueError(f"{ref.role} on {ref.target} has no accepted geometry.")


def get(engine: Any, document: Any, meshes: Any, target: str | SurfaceReference) -> SurfaceProvider:
    value = snapshot(engine, document, meshes, target)
    if not value.resource.mesh.counts[3]:
        ref = value.reference
        raise ValueError(f"{ref.role} on {ref.target} is empty; adjust its construction or crop.")
    return value


def inputs(engine: Any, document: Any, meshes: Any, targets: Any) -> tuple[Any, Any]:
    providers = [get(engine, document, meshes, target) for target in targets]
    return [p.resource.mesh.handle for p in providers], [p.frame for p in providers]


def query_references(
    engine: Any, document: Any, meshes: Any, targets: Any
) -> tuple[SurfaceReference, ...]:
    providers = [snapshot(engine, document, meshes, target) for target in targets]
    return tuple(p.reference for p in providers if p.resource.mesh.counts[3])


def ports(document: Any, targets: Any) -> set[Port]:
    refs = [normalize(document, target) for target in targets]
    return {anatomical_surfaces.port(r) for r in refs} | {Port(r.target, "pose") for r in refs}


def triangle_count(document: Any, meshes: Any, ref: SurfaceReference) -> int:
    item = document.registry.anatomy.get(ref.target)
    if item is None:
        return 0
    result = anatomical_surfaces.result(item, ref.role)
    key = geometry_asset(item) if isinstance(item, SCP) else result.asset
    return meshes[key].mesh.counts[3] if key in meshes else 0


def binding_frames(
    provider: SurfaceProvider, meshes: Any, reference: str, records: Any, cancel: int
) -> Any:
    from anthroforge.native import material_bindings

    if not reference and provider.reference.role != "SCP_GEOMETRY":
        raise ValueError("Tissue binding has no retained material reference; explicitly rebind.")
    reference = reference or provider.asset_id
    if reference not in meshes:
        raise ValueError("Missing retained material reference; explicitly rebind the attachment.")
    return material_bindings.frames(
        meshes[reference].mesh, provider.resource.mesh, provider.frame, records, cancel
    )
