"""Owned bind-time dense geometry; consumers resolve it without mutating authored definitions."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult, geometry_asset
from anthroforge.native import attachment_fields, curve_editing
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.scene import entity_frame

from .path_assets import PathAsset


@dataclass(frozen=True, eq=False)
class AttachmentAsset:
    targets: tuple[str, ...]
    field: attachment_fields.Field


def surface_inputs(engine: GeometryEngine, document: Document, meshes: Any, targets: Any) -> Any:
    entities = [document.entity(key) for key in targets]
    if any(not geometry_asset(item) or geometry_asset(item) not in meshes for item in entities):
        raise ValueError("Required anatomical surface has no accepted geometry.")
    return (
        [meshes[geometry_asset(item)].mesh.handle for item in entities],
        [entity_frame(engine, item) for item in entities],
    )


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
