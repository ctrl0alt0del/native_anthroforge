"""Accepted paths retain the authored inputs needed by downstream control deformers."""

from dataclasses import dataclass, replace

from anthroforge.core.construction import Curve
from anthroforge.core.results import EvaluationResult
from anthroforge.native import paths
from anthroforge.native.mesh import GeometryEngine


@dataclass(frozen=True)
class PathAsset:
    path: paths.Path
    authored: Curve


def evaluate(engine: GeometryEngine, curve: Curve, cancel: int = 0) -> PathAsset:
    # Result history is not recursively embedded in accepted input snapshots.
    authored = replace(curve, result=EvaluationResult())
    return PathAsset(paths.evaluate(engine, authored, cancel), authored)
