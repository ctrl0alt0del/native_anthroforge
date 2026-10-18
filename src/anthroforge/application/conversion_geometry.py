"""Owned conversion inputs; numerical resampling remains in the native path engine."""

from collections.abc import Sequence
from dataclasses import dataclass, replace

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_conversion import ConversionSpec
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import EvaluationResult
from anthroforge.native import paths
from anthroforge.native.mesh import GeometryEngine

from .path_assets import PathAsset


@dataclass(frozen=True)
class ConversionInput:
    source: Curve
    spec: ConversionSpec
    asset: PathAsset | None


def convert(engine: GeometryEngine, value: ConversionInput, cancel: int) -> Curve:
    spec, source = value.spec, value.source
    if spec.mode == "EVALUATED":
        points = sampled_points(value, cancel)
    else:
        points = authored_points(source, spec)
    return replace(source, points=points, engine_settings=spec.settings, result=EvaluationResult())


def authored_points(source: Curve, spec: ConversionSpec) -> tuple[CurvePoint, ...]:
    selected = set(spec.points)
    if not isinstance(spec.settings, RoutingSettings):
        return source.points
    if selected - {p.id for p in source.points}:
        raise ValueError("Routing constraints must name authored curve points.")
    if not source.closed and not {source.points[0].id, source.points[-1].id} <= selected:
        raise ValueError("An open route must retain both endpoints.")
    if isinstance(source, Fiber) and not {b.point for b in source.bindings} <= selected:
        raise ValueError("Retain every anatomically bound point as a routing constraint.")
    return tuple(point for point in source.points if point.id in selected)


def sampled_points(value: ConversionInput, cancel: int) -> tuple[CurvePoint, ...]:
    if value.asset is None:
        raise ValueError("Conversion needs an accepted path; evaluate the curve first.")
    source, count = value.source, value.spec.samples
    if isinstance(source, Fiber) and any(
        b.point not in endpoint_ids(source) for b in source.bindings
    ):
        raise ValueError("Use authored conversion to retain interior anatomical bindings.")
    rows = paths.sample(value.asset.path, count, 0, 1, IDENTITY, cancel=cancel)
    points = tuple(sample_point(row) for row in rows)
    return preserve_endpoints(source, points)


def endpoint_ids(source: Curve) -> set[str]:
    return {source.points[0].id} if source.closed else {source.points[0].id, source.points[-1].id}


def sample_point(row: Sequence[float]) -> CurvePoint:
    values = tuple(row)
    return CurvePoint(
        position=values[:3],
        left_mode="VECTOR",
        right_mode="VECTOR",
        radius=values[9],
        tilt=values[10],
    )


def preserve_endpoints(source: Curve, points: tuple[CurvePoint, ...]) -> tuple[CurvePoint, ...]:
    points = (replace(points[0], id=source.points[0].id), *points[1:])
    if not source.closed:
        points = (*points[:-1], replace(points[-1], id=source.points[-1].id))
    return points
