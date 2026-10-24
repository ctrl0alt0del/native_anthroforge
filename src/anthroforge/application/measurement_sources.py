"""Frozen witness addresses distinguish accepted stages, anatomical roles and spatial instances."""

from dataclasses import replace
from typing import Any

from anthroforge.core.mirroring import parse, source
from anthroforge.core.results import geometry_asset
from anthroforge.native import construction, scene

from . import surface_providers, tissue_inspection_stages
from .object_frames import Frames


def resolve(context: Any, entity: str, role: str = "", stage: str = "") -> dict[str, Any]:
    item = context.document.object(source(entity))
    if parse(entity) and entity not in context.document.mirrors.instances:
        raise ValueError("The measured mirrored instance is unavailable.")
    if stage:
        return explicit_stage(context, entity, stage, role)
    if item.id in context.document.registry.anatomy:
        return anatomy(context, entity, role)
    if role:
        raise ValueError("This construction surface does not expose an anatomical surface role.")
    return construction_surface(context, entity, item)


def explicit_stage(context: Any, entity: str, stage: str, role: str) -> dict[str, Any]:
    if role:
        raise ValueError("Choose a surface role or an explicit tissue stage, not both.")
    return tissue_stage(context, entity, stage)


def anatomy(context: Any, entity: str, role: str) -> dict[str, Any]:
    reference = surface_providers.normalize(context.document, entity)
    provider = surface_providers.get(
        context.engine,
        context.document,
        context.assets,
        replace(reference, role=role or reference.role),
    )
    return metadata(
        entity, provider.asset_id, provider.frame, provider.result.revision, provider.reference.role
    )


def metadata(
    entity: str, asset: str, frame: Any, revision: int, role: str = "", stage: str = ""
) -> dict[str, Any]:
    return dict(
        entity=entity, asset=asset, frame=tuple(frame), revision=revision, role=role, stage=stage
    )


def tissue_stage(context: Any, entity: str, stage: str) -> dict[str, Any]:
    item = tissue_inspection_stages.tissue(context, entity)
    tissue_inspection_stages.mesh(context, entity, stage)
    result = tissue_inspection_stages.result(item, stage)
    frame = tissue_inspection_stages.instance_frame(context, entity, stage)
    return metadata(entity, result.asset, frame, result.revision, stage=stage)


def construction_surface(context: Any, entity: str, item: Any) -> dict[str, Any]:
    asset = geometry_asset(item)
    if asset not in context.assets:
        raise ValueError("The selected object has no accepted mesh surface.")
    frame = Frames(context.engine, context.document).world(item.id)
    instance = parse(entity)
    if instance:
        frame = construction.matrix(
            context.engine, context.document.mirrors.plane(instance).frame, frame
        )
    frame = scene.geometry_matrix(
        context.engine, frame, getattr(item, "geometry_offset", (0, 0, 0))
    )
    return metadata(entity, asset, frame, item.result.revision)
