"""Resolve a selected limb from its captured attachment and source polygon."""

from typing import Any

import numpy as np

from anthroforge.core.entities import IDENTITY
from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.results import geometry_asset
from anthroforge.native.attachments import anchor_points
from anthroforge.native.scene import entity_frame


def dimensions(engine: Any, item: Any, meshes: Any) -> float:
    binding = item.attachment.binding
    if not binding or item.attachment.child_mode != "FACE_CENTER":
        raise ValueError(f"{item.name}: automatic radius needs a captured attachment face.")
    mesh = meshes[geometry_asset(item)].mesh
    idx = int(binding[27])
    offsets = mesh.array(2)
    if not 0 <= idx < len(offsets) - 1:
        raise ValueError(f"{item.name}: attachment polygon is unavailable.")
    ring = mesh.array(0)[mesh.array(1)[offsets[idx] : offsets[idx + 1]]]
    linear = np.asarray(entity_frame(engine, item)).reshape(4, 4)[:3, :3]
    radius = float(np.linalg.norm((ring - ring.mean(axis=0)) @ linear.T, axis=1).max())
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError(f"{item.name}: attachment polygon has no measurable radius.")
    return radius


def attached_points(request: Any, item: Any) -> Any:
    parent = request.document.index.entities.get(item.parent)
    if parent is None or not item.attachment.binding:
        raise ValueError(f"{item.name}: limb needs a captured parent-child attachment.")
    assets = request.resources.meshes
    surface, ref = assets.get(geometry_asset(parent)), assets.get(item.attachment.material_asset)
    return anchor_points(
        request.engine,
        item,
        parent,
        surface.mesh.handle if surface else 0,
        ref.mesh.handle if ref else 0,
    )


def anchors(request: Any, item: Any, instance: str) -> tuple[Any, Any, Any]:
    points = attached_points(request, item)
    mirror = MirrorInstance(item.id, instance)
    reflection = request.document.mirrors.plane(mirror).frame if instance else IDENTITY
    matrix = np.asarray(reflection).reshape(4, 4)
    child, support = np.asarray(points).reshape(2, 3) @ matrix[:3, :3].T + matrix[:3, 3]
    return child, support, matrix[:3, :3]


def settings(request: Any, src: Any, declaration: Any, base: Any) -> dict[str, Any]:
    item = request.document.index.entities[src.owner]
    child, support, _ = anchors(request, item, src.instance)
    shape = declaration.limb
    radius = limb_radius(request, item, shape, base)
    result = dict(
        child_point=child.tolist(),
        parent_point=support.tolist(),
        boundary_radius=shape.boundary_radius or 0.75 * radius,
    )
    if base is None:
        rest = shape.rest_radius or radius
        return result | dict(rest_radius=rest, material_length_ratio=0.4 * rest / radius)
    return result | {key: base[key] for key in ("rest_radius", "material_length_ratio")}


def limb_radius(request: Any, item: Any, shape: Any, base: Any) -> float:
    if base and shape.boundary_radius is not None:
        return float(shape.boundary_radius)
    if item.attachment.child_mode == "FACE_CENTER":
        return dimensions(request.engine, item, request.resources.meshes)
    if shape.boundary_radius is None or (base is None and shape.rest_radius is None):
        raise ValueError(f"{item.name}: automatic radius needs a captured attachment face.")
    # Manual-only attachments have no anatomical face. Use the default aperture-to-radius ratio.
    return float(shape.boundary_radius) / 0.75
