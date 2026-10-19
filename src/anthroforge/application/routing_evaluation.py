"""Routing consumes accepted surface snapshots; the native engine owns all numerical work."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import EvaluationResult
from anthroforge.core.routing_obstacles import references
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import routing

from . import curve_sources, surface_providers
from .path_assets import PathAsset


def owners(item: Curve, surfaces: tuple[SurfaceReference, ...]) -> tuple[int, ...]:
    bindings = (
        {b.point: surfaces.index(b.reference) + 1 for b in item.bindings}
        if isinstance(item, Fiber)
        else {}
    )
    return tuple(bindings.get(point.id, 0) for point in item.points)


def warm_path(item: Curve, asset: PathAsset | None) -> Any:
    if asset is None or asset.authored.engine != "ROUTED":
        return None
    before, after = warm_identity(asset.authored), warm_identity(item)
    return asset.path if before == after else None


def warm_identity(item: Curve) -> tuple[Any, ...]:
    bindings = (
        tuple((b.point, b.reference) for b in item.bindings) if isinstance(item, Fiber) else ()
    )
    return tuple(point.id for point in item.points), bindings, item.closed


def evaluate(
    engine: Any, document: Any, resources: Any, item: Curve, cancel: int, warm: Any = None
) -> PathAsset:
    surfaces = surface_providers.query_references(
        engine, document, resources.meshes, references(document, item)
    )
    handles, matrices = surface_providers.inputs(engine, document, resources.meshes, surfaces)
    frame = curve_sources.world(engine, document, item.id)
    warm = warm_path(item, warm or resources.paths.get(item.result.asset))
    inputs = routing.Inputs(
        item, tuple(handles), tuple(matrices), frame, owners(item, surfaces), warm
    )
    path, report = routing.evaluate(engine, inputs, cancel)
    return PathAsset(path, replace(item, result=EvaluationResult()), report)
