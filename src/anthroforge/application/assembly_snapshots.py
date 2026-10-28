"""Retain only external surface evidence needed for source-independent reference repair."""

import zipfile
from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import anatomical_surfaces
from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset
from anthroforge.core.surface_references import SurfaceReference

from . import resource_storage, surface_providers


def retain(preparation: Any) -> None:
    source = preparation.source
    with zipfile.ZipFile(source.path) as archive:
        for index, row in enumerate(preparation.mapping.references):
            if any(use.relationship == "support" and use.role for use in row.uses):
                preparation.mapping.references[index] = snapshot(preparation, archive, row)


def snapshot(p: Any, archive: Any, row: Any) -> Any:
    source = p.source.document
    declaration = next((r for r in source.external_references if r.id == row.source_entity), None)
    if declaration is not None:
        return retained_snapshot(p, archive, row, declaration)
    role = next(use.role for use in row.uses if use.role)
    item = source.object(row.source_entity)
    key = surface_asset(item, role)
    load(p, archive, key)
    provider = surface_providers.snapshot(
        p.engine, source, p.loaded.meshes, SurfaceReference(item.id, role, row.source_instance)
    )
    return replace(row, surface_asset=p.assets[key], surface_frame=provider.frame)


def surface_asset(item: Any, role: str) -> str:
    return (
        geometry_asset(item)
        if isinstance(item, SCP)
        else anatomical_surfaces.result(item, role).asset
    )


def retained_snapshot(p: Any, archive: Any, row: Any, original: Any) -> Any:
    if not original.surface_asset:
        return row
    load(p, archive, original.surface_asset)
    return replace(
        row, surface_asset=p.assets[original.surface_asset], surface_frame=original.surface_frame
    )


def load(p: Any, archive: Any, key: str) -> None:
    if not key:
        raise ValueError("The source has no accepted surface for this external reference.")
    if key not in p.loaded.meshes:
        metadata = p.source.metadata["assets"][key]
        p.loaded.meshes[key] = resource_storage.read_mesh(archive, key, metadata, p.engine)
    if key not in p.assets:
        p.assets[key] = str(uuid4())
        p.resources.meshes[p.assets[key]] = p.loaded.meshes[key]
