"""Propagation policy uses the shared attachment service and owned native preparation."""

from typing import Any

from anthroforge.native import fiber_deformation

from . import attachment_assets, surface_providers


def resolve(engine: Any, document: Any, resources: Any, item: Any, asset: Any,
            cancel: int, method: str) -> Any:
    if method == "LOCAL_SURFACE":
        return attachment_assets.resolved_points(engine, document, resources.meshes, asset, cancel)
    if method != "SMOOTH_SHAPE":
        raise ValueError("Unknown fiber propagation method.")
    pins = sorted(i for i, p in enumerate(item.points) if any(b.point == p.id for b in item.bindings))
    meshes = [resources.meshes[t.material_asset].mesh for t in asset.targets]
    references = [t.reference for t in asset.targets]
    groups = [references.index(ref) for ref in references]
    prepared = fiber_deformation.prepare(engine, asset.field, meshes, pins, groups, cancel)
    providers = [surface_providers.get(engine, document, resources.meshes, t.reference) for t in asset.targets]
    goals = pin_goals(engine, resources.meshes, asset, providers, pins, cancel)
    return fiber_deformation.evaluate(prepared, [p.resource.mesh.handle for p in providers],
                                      [p.frame for p in providers], goals, cancel)


def pin_goals(engine: Any, meshes: Any, asset: Any, providers: Any, pins: Any, cancel: int) -> Any:
    import numpy as np

    field = asset.field
    rows = [field.path.count + 3 * p for p in pins]
    frames = np.zeros((len(rows), 2, 16))
    for index, (surface, provider) in enumerate(zip(asset.targets, providers, strict=True)):
        mask = (field.owners[rows] == index) & (field.weights[rows] > 0)
        if mask.any():
            frames[mask] = surface_providers.binding_frames(provider, meshes, surface.material_asset,
                                                           field.bindings[rows][mask], cancel)
    return blend_pins(engine, field, rows, frames, cancel)


def blend_pins(engine: Any, field: Any, rows: Any, frames: Any, cancel: int) -> Any:
    import numpy as np

    from anthroforge.native.mesh import doubles, pointer

    frames, weights = doubles(frames), doubles(field.weights[rows])
    output = np.empty((len(rows), 3))
    engine.check(engine.library.af_attachment_blend_frames(len(rows), pointer(frames),
                                                           pointer(weights), pointer(output), cancel))
    return output
