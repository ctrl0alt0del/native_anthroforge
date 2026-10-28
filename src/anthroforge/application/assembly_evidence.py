"""World-space attachment evidence and retained surfaces for source-independent repair."""

from typing import Any

from anthroforge.core.assembly import declaration
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import attachments, material_bindings

from .surface_providers import SurfaceProvider


def retained_provider(document: Any, resources: Any, reference: Any) -> Any:
    value = declaration(document.registry.records, reference.target)
    if value is None:
        return None
    if not value.surface_asset or value.surface_asset not in resources.meshes:
        raise ValueError("No retained surface evidence; select an explicit rebind target.")
    return SurfaceProvider(
        reference,
        resources.meshes[value.surface_asset],
        value.surface_frame,
        EvaluationResult(value.surface_asset),
        Port(value.id, "geometry"),
        value.surface_asset,
    )


def locations(
    engine: Any, item: Any, provider: Any, meshes: Any, cancel: int, document: Any, batches: Any
) -> list[dict[str, Any]]:
    if isinstance(item, Fiber):
        return fiber_locations(item, provider, meshes, cancel)
    if isinstance(item, Anchor):
        return [anchor_location(item, provider, meshes, cancel)]
    if isinstance(item, SCP):
        return scp_location(engine, item, provider, meshes, document)
    if isinstance(item, TissueVCP):
        return region_locations(item, provider, meshes, batches, cancel)
    return []


def fiber_locations(item: Any, provider: Any, meshes: Any, cancel: int) -> list[Any]:
    return [
        location(b.point, b.reference, b.material_asset, b.attachment, provider, meshes, cancel)
        for b in item.bindings
        if b.attachment
    ]


def scp_location(engine: Any, item: Any, provider: Any, meshes: Any, document: Any) -> list[Any]:
    if not item.parent or not item.attachment.binding:
        return []
    ref = SurfaceReference(item.parent, instance=item.attachment.parent_instance)
    surface = provider(ref) if item.attachment.parent_mode != "OBJECT_ORIGIN" else None
    points = scp_points(engine, item, surface, meshes, document)
    return [
        dict(
            point=item.id,
            target=item.parent,
            role=ref.role,
            position=points[3:],
            requested=points[:3],
        )
    ]


def scp_points(engine: Any, item: Any, surface: Any, meshes: Any, document: Any) -> Any:
    key = item.attachment.material_asset
    handle = surface.resource.mesh.handle if surface else 0
    material = meshes[key].mesh.handle if key else handle
    return attachments.anchor_points(
        engine,
        item,
        document.entity(item.parent),
        handle,
        material,
    )


def region_locations(item: Any, provider: Any, meshes: Any, batches: Any, cancel: int) -> list[Any]:
    return [
        entry
        for row in item.constraints
        if row.reference is not None
        for entry in region(row, provider, meshes, batches, cancel)
    ]


def region(row: Any, provider: Any, meshes: Any, batches: Any, cancel: int) -> list[Any]:
    records = batches[row.binding_asset].records
    indices = range(0, len(records), max(1, (len(records) + 15) // 16))
    surface = provider(row.reference)
    frames = material_bindings.frames(
        meshes[row.material_asset].mesh,
        surface.resource.mesh,
        surface.frame,
        records[list(indices)],
        cancel,
    )
    return [
        region_point(row, i, frame, len(records)) for i, frame in zip(indices, frames, strict=True)
    ]


def region_point(row: Any, index: int, frame: Any, count: int) -> dict[str, Any]:
    return dict(
        point=f"{row.id}:{index}",
        target=row.reference.target,
        role=row.reference.role,
        position=frame[[3, 7, 11]].tolist(),
        region_samples=count,
    )


def anchor_location(item: Any, provider: Any, meshes: Any, cancel: int) -> dict[str, Any]:
    value = item.binding
    return location(
        item.id, value.reference, value.material_asset, value.attachment, provider, meshes, cancel
    )


def location(
    point: str, ref: Any, asset: str, attachment: Any, provider: Any, meshes: Any, cancel: int
) -> dict[str, Any]:
    surface = provider(ref)
    material = meshes[asset].mesh if asset else surface.resource.mesh
    frame = material_bindings.frames(
        material, surface.resource.mesh, surface.frame, [attachment.binding], cancel
    )[0]
    return dict(
        point=point,
        target=ref.target,
        role=ref.role,
        instance=ref.instance,
        position=frame[[3, 7, 11]].tolist(),
    )
