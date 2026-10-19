"""Owned bind-time dense geometry; consumers resolve it without mutating authored definitions."""

from dataclasses import dataclass, replace
from typing import Any

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


@dataclass(frozen=True)
class ResolvedSurfaces:
    meshes: tuple[Any, ...]
    frames: tuple[Any, ...]

    def __iter__(self) -> Any:
        return iter(([mesh.handle for mesh in self.meshes], self.frames))


def captures(engine: Any, document: Any, meshes: Any, targets: Any) -> tuple[CapturedSurface, ...]:
    providers = [surface_providers.get(engine, document, meshes, ref) for ref in targets]
    return tuple(CapturedSurface(p.reference, p.asset_id) for p in providers)


def captured_inputs(
    engine: Any, document: Any, meshes: Any, asset: AttachmentAsset, cancel: int
) -> ResolvedSurfaces:
    providers = [
        surface_providers.get(engine, document, meshes, s.reference) for s in asset.targets
    ]
    resolved = tuple(
        surface_providers.binding_mesh(
            p, meshes, s.material_asset, owner_records(asset.field, i), cancel
        )
        for i, (p, s) in enumerate(zip(providers, asset.targets, strict=True))
    )
    return ResolvedSurfaces(resolved, tuple(p.frame for p in providers))


def owner_records(field: attachment_fields.Field, index: int) -> Any:
    return field.bindings[(field.owners == index) & (field.weights > 0)]


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
