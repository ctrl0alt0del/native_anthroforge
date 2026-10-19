"""Owned bind-time dense geometry; consumers resolve it without mutating authored definitions."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult
from anthroforge.native import attachment_fields, curve_editing
from anthroforge.native.mesh import GeometryEngine

from . import surface_providers
from .path_assets import PathAsset


@dataclass(frozen=True, eq=False)
class AttachmentAsset:
    targets: tuple[str, ...]
    field: attachment_fields.Field


def surface_inputs(engine: GeometryEngine, document: Document, meshes: Any, targets: Any) -> Any:
    return surface_providers.inputs(engine, document, meshes, targets)


def compact(field: attachment_fields.Field, targets: tuple[str, ...]) -> AttachmentAsset:
    changed, used = attachment_fields.compact(field, len(targets))
    return AttachmentAsset(tuple(targets[index] for index in used), changed)


def evaluate(
    engine: GeometryEngine,
    item: Curve,
    asset: AttachmentAsset,
    surfaces: Any,
    world: Any,
    cancel: int,
) -> PathAsset:
    path, records = attachment_fields.resolve(engine, surfaces, asset.field, world, cancel)
    points = tuple(
        curve_editing.unpack(old, row) for old, row in zip(item.points, records, strict=True)
    )
    return PathAsset(path, replace(item, points=points, result=EvaluationResult()))
