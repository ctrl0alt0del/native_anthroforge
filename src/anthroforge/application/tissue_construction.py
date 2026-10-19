"""Dispatch native strategies from accepted typed bases, never from source previews."""

from typing import Any

from anthroforge.core.tissue_parts import active
from anthroforge.native import paths, tissue_parts, tissue_shapes, tissue_smoothing
from anthroforge.native.mesh import Mesh

from .tissue_output import TissueOutput


def construct(engine: Any, resources: Any, item: Any, cancel: int) -> TissueOutput:
    settings = item.parts[0].a.inflation
    if item.base_state.kind == "POINT":
        mesh = tissue_shapes.radial(
            engine, item.base_state.frame, settings, item.resolution, cancel
        )
        return TissueOutput(mesh=mesh, diagnostics=())
    if item.base_state.kind == "CURVE":
        return TissueOutput(mesh=sweep(engine, resources, item, cancel), diagnostics=())
    mesh = resources.meshes[item.base_result.asset].mesh
    if settings.mode == "NORMAL":
        return normal(mesh, item, cancel)
    return muscle(mesh, item, cancel)


def normal(mesh: Mesh, item: Any, cancel: int) -> TissueOutput:
    field = next((f.values for f in item.fields if f.name == "INFLATION"), ())
    result = tissue_shapes.normal(mesh, item.parts[0].a.inflation, field, item.reverse, cancel)
    return TissueOutput(mesh=result, diagnostics=())


def muscle(mesh: Mesh, item: Any, cancel: int) -> TissueOutput:
    parts = active(item)
    first, reports = muscle_side(mesh, parts, "a", item.reverse, item.both_sides, cancel)
    if not item.both_sides:
        return TissueOutput(mesh=first, diagnostics=reports)
    second, other = muscle_side(mesh, parts, "b", not item.reverse, True, cancel)
    result = tissue_parts.compose(first, second, item.reverse, cancel)
    return TissueOutput(mesh=result, diagnostics=reports + other)


def muscle_side(
    mesh: Mesh, parts: Any, side: str, reverse: bool, envelope: bool, cancel: int
) -> Any:
    own = tissue_parts.evaluate(mesh, parts, side, reverse, cancel, envelope)
    return tissue_smoothing.evaluate(mesh, own, parts, side, cancel)


def sweep(engine: Any, resources: Any, item: Any, cancel: int) -> Mesh:
    path = resources.paths[item.base_result.asset].path
    samples = paths.sample(path, item.resolution, 0, 1, item.base_state.frame, False, cancel)
    return tissue_shapes.sweep(
        engine, samples, path.closed, item.parts[0].a.inflation, item.reverse, cancel
    )
