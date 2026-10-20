"""Owned bind-time dense geometry; consumers resolve it without mutating authored definitions."""

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surface_references import CapturedSurface
from anthroforge.native import attachment_fields, curve_editing
from anthroforge.native.mesh import GeometryEngine

from . import surface_providers
from .path_assets import PathAsset


@dataclass(frozen=True, eq=False)
class AttachmentAsset:
    targets: tuple[CapturedSurface, ...]
    field: attachment_fields.Field


def surface_inputs(engine: GeometryEngine, document: Document, meshes: Any, targets: Any) -> Any:
    return surface_providers.inputs(engine, document, meshes, targets)


def compact(
    field: attachment_fields.Field, targets: tuple[CapturedSurface, ...]
) -> AttachmentAsset:
    changed, used = attachment_fields.compact(field, len(targets))
    return AttachmentAsset(tuple(targets[index] for index in used), changed)


def captures(engine: Any, document: Any, meshes: Any, targets: Any) -> tuple[CapturedSurface, ...]:
    providers = [surface_providers.get(engine, document, meshes, ref) for ref in targets]
    return tuple(CapturedSurface(p.reference, p.asset_id) for p in providers)


def resolved_points(
    engine: Any, document: Any, meshes: Any, asset: AttachmentAsset, cancel: int
) -> Any:
    field = asset.field
    frames = np.zeros((*field.owners.shape, 16))
    for index, surface in enumerate(asset.targets):
        provider = surface_providers.get(engine, document, meshes, surface.reference)
        mask = (field.owners == index) & (field.weights > 0)
        frames[mask] = surface_providers.binding_frames(
            provider, meshes, surface.material_asset, field.bindings[mask], cancel
        )
    return attachment_fields.blend_frames(engine, field, frames, cancel)


def evaluate(
    engine: GeometryEngine,
    item: Curve,
    asset: AttachmentAsset,
    positions: Any,
    world: Any,
    cancel: int,
) -> PathAsset:
    path, records = attachment_fields.from_positions(engine, positions, asset.field, world, cancel)
    points = tuple(
        curve_editing.unpack(old, row) for old, row in zip(item.points, records, strict=True)
    )
    return PathAsset(path, replace(item, points=points, result=EvaluationResult()))
