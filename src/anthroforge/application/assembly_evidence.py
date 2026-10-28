"""World-space attachment evidence and retained surfaces for source-independent repair."""

from typing import Any

from anthroforge.core.assembly import declaration
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.native import material_bindings

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


def locations(item: Any, provider: Any, meshes: Any, cancel: int) -> list[dict[str, Any]]:
    if isinstance(item, Fiber):
        return [
            location(b.point, b.reference, b.material_asset, b.attachment, provider, meshes, cancel)
            for b in item.bindings
            if b.attachment
        ]
    if isinstance(item, Anchor):
        return [anchor_location(item, provider, meshes, cancel)]
    return []


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
