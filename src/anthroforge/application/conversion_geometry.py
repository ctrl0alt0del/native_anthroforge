"""Owned conversion inputs; numerical resampling remains in the native path engine."""

from collections.abc import Sequence
from dataclasses import dataclass, replace

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_conversion import ConversionSpec
from anthroforge.core.curve_engines import RoutingSettings
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
    if not {p.id for p in source.points if p.junction} <= selected:
        raise ValueError("Retain every shared junction point as a routing constraint.")
    return tuple(point for point in source.points if point.id in selected)


def sampled_points(value: ConversionInput, cancel: int) -> tuple[CurvePoint, ...]:
    if value.asset is None:
        raise ValueError("Conversion needs an accepted path; evaluate the curve first.")
    retained = retained_points(value)
    rows, indices = paths.sample_anchored(
        value.asset.path, value.spec.samples, [i for i, _ in retained], cancel
    )
    points = tuple(sample_point(row) for row in rows)
    identities = {int(index): key for index, (_, key) in zip(indices, retained, strict=True)}
    return preserved_points(value.source, points, identities)


def preserved_points(
    source: Curve, points: tuple[CurvePoint, ...], identities: dict[int, str]
) -> tuple[CurvePoint, ...]:
    shared = {p.id: p.junction for p in source.points}
    return tuple(
        replace(p, id=identities.get(i, p.id), junction=shared.get(identities.get(i, ""), ""))
        for i, p in enumerate(points)
    )


def retained_points(value: ConversionInput) -> tuple[tuple[int, str], ...]:
    assert value.asset is not None
    source = value.source
    keys = endpoint_ids(source) | {p.id for p in source.points if p.junction}
    if isinstance(source, Fiber):
        keys |= {b.point for b in source.bindings}
    accepted = value.asset.authored.points
    if keys - {p.id for p in accepted}:
        raise ValueError("Evaluate pending structural point changes before sampled conversion.")
    return tuple((i, p.id) for i, p in enumerate(accepted) if p.id in keys)


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
