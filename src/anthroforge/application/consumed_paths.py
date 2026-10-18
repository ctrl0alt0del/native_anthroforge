"""Consumer placement uses accepted curve construction and current declared transforms."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve, ResolvedPrimitive
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.primitive_sampling import count
from anthroforge.native import paths
from anthroforge.native.mesh import GeometryEngine

from . import curve_sources
from .path_assets import PathAsset


def accepted(document: Document, resources: dict[str, PathAsset], curve: str) -> PathAsset:
    key = curve_sources.source(document, curve).result.asset
    if not key or key not in resources:
        raise ValueError("Required curve has no accepted path: " + curve)
    return resources[key]


def definition(
    engine: GeometryEngine, document: Document, entity: SCP, resources: dict[str, PathAsset]
) -> ResolvedPrimitive:
    authored = curve_sources.resolve(engine, document, entity)
    curves = tuple(
        replace(
            accepted(document, resources, c.id).authored,
            matrix=c.matrix,
            start=c.start,
            span=c.span,
        )
        for c in authored.curves
    )
    return replace(authored, curves=curves, samples=count(entity.primitive))


def samples(
    path: paths.Path, curve: Curve, definition: ResolvedPrimitive, reverse: bool, cancel: int
) -> Any:
    if definition.kind == "BODY":
        return paths.body(path, len(curve.points) - 1 if curve.closed else 0, reverse, cancel)
    start = definition.start if curve.start is None else curve.start
    span = definition.span if curve.span is None else curve.span
    return paths.sample(path, definition.samples, start, span, curve.matrix, reverse, cancel)
