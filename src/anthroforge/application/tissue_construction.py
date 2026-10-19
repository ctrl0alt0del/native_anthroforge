"""Dispatch native strategies from accepted typed bases, never from source previews."""

from typing import Any

from anthroforge.core.tissue_parts import active
from anthroforge.native import paths, tissue_parts, tissue_shapes
from anthroforge.native.mesh import Mesh


def construct(engine: Any, resources: Any, item: Any, cancel: int) -> Mesh:
    settings = item.parts[0].a.inflation
    if item.base_state.kind == "POINT":
        return tissue_shapes.radial(
            engine, item.base_state.frame, settings, item.resolution, cancel
        )
    if item.base_state.kind == "CURVE":
        return sweep(engine, resources, item, cancel)
    mesh = resources.meshes[item.base_result.asset].mesh
    if settings.mode == "NORMAL":
        field = next((f.values for f in item.fields if f.name == "INFLATION"), ())
        return tissue_shapes.normal(mesh, settings, field, item.reverse, cancel)
    return muscle(mesh, item, cancel)


def muscle(mesh: Mesh, item: Any, cancel: int) -> Mesh:
    parts = active(item)
    first = tissue_parts.evaluate(mesh, parts, "a", item.reverse, cancel)
    if not item.both_sides:
        return first
    second = tissue_parts.evaluate(mesh, parts, "b", not item.reverse, cancel)
    return tissue_parts.compose(first, second, item.reverse, cancel)


def sweep(engine: Any, resources: Any, item: Any, cancel: int) -> Mesh:
    path = resources.paths[item.base_result.asset].path
    samples = paths.sample(path, item.resolution, 0, 1, item.base_state.frame, False, cancel)
    return tissue_shapes.sweep(
        engine, samples, path.closed, item.parts[0].a.inflation, item.reverse, cancel
    )
