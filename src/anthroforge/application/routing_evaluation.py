"""Routing consumes accepted surface snapshots; the native engine owns all numerical work."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.curve_dependencies import targets
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import EvaluationResult
from anthroforge.native import routing

from . import attachment_assets, curve_sources
from .path_assets import PathAsset


def owners(item: Curve, surfaces: tuple[str, ...]) -> tuple[int, ...]:
    bindings = (
        {b.point: surfaces.index(b.target) + 1 for b in item.bindings}
        if isinstance(item, Fiber)
        else {}
    )
    return tuple(bindings.get(point.id, 0) for point in item.points)


def warm_path(item: Curve, asset: PathAsset | None) -> Any:
    if asset is None or asset.authored.engine != "ROUTED":
        return None
    before = tuple(point.id for point in asset.authored.points)
    after = tuple(point.id for point in item.points)
    return asset.path if before == after else None


def evaluate(
    engine: Any, document: Any, resources: Any, item: Curve, cancel: int, warm: Any = None
) -> PathAsset:
    surfaces = tuple(sorted(targets(item)))
    handles, matrices = attachment_assets.surface_inputs(
        engine, document, resources.meshes, surfaces
    )
    frame = curve_sources.world(engine, document, item.id)
    warm = warm_path(item, warm or resources.paths.get(item.result.asset))
    inputs = routing.Inputs(
        item, tuple(handles), tuple(matrices), frame, owners(item, surfaces), warm
    )
    path, report = routing.evaluate(engine, inputs, cancel)
    return PathAsset(path, replace(item, result=EvaluationResult()), report)
