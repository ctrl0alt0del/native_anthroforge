"""Tissue lifecycle and typed configuration shared by desktop and headless authoring."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core import tissue_policy
from anthroforge.core.membranes import Membrane
from anthroforge.core.tissue_settings import TissueInflation, TissuePart, TissueSide
from anthroforge.core.tissues import TissueVCP

from . import object_operations, tissue_codec, tissue_tasks
from .operations import require_name


def create(session: Any, source: str, name: str = "Tissue", preset: str = "MUSCLE") -> str:
    source_item = object_operations.editable(session, source)
    item = definition(source_item, name, preset)
    tissue_policy.validate(item, session.document.registry.records)
    session.replace_document(objects=(*session.document.objects, item))
    tissue_tasks.schedule(session, {item.id}, explicit=True)
    return item.id


def definition(source_item: Any, name: str, preset: str) -> TissueVCP:
    domain = tissue_policy.domain(source_item)
    mode = {"POINT": "RADIAL", "CURVE": "PROFILE", "SURFACE": "NORMAL"}[domain]
    if preset == "MUSCLE" and isinstance(source_item, Membrane) and source_item.kind != "PATCH":
        mode = "DISTRIBUTED"
    return TissueVCP(
        name=require_name(name),
        source=source_item.id,
        preset=preset,
        classification="MUSCLE" if preset == "MUSCLE" else "SOFT_TISSUE",
        parts=(TissuePart(a=TissueSide(TissueInflation(mode=mode))),),
        stacking=preset == "MUSCLE" and domain == "SURFACE",
        owners=source_item.owners,
    )


def tissue(session: Any, target: str) -> TissueVCP:
    item = object_operations.editable(session, target)
    if not isinstance(item, TissueVCP):
        raise ValueError("Select an anatomical Tissue.")
    return item


def configure(session: Any, target: str, changes: dict[str, Any]) -> None:
    item = tissue(session, target)
    allowed = {"classification", "color", "both_sides", "reverse", "stacking", "resolution"}
    if set(changes) - allowed:
        raise ValueError("Unsupported tissue setting; use the dedicated strategy operation.")
    if "resolution" in changes and changes["resolution"] != item.resolution:
        from .construction_policy import require_topology_edit

        require_topology_edit(session.document, target)
    updated = replace(item, **changes)
    tissue_policy.validate(updated, session.document.registry.records)
    object_operations.install(session, updated)


def inflation(
    session: Any, target: str, changes: dict[str, Any], part: str = "main", side: str = "a"
) -> None:
    item = tissue(session, target)
    if side not in ("a", "b") or part not in {p.id for p in item.parts}:
        raise ValueError("Choose an existing tissue part and side.")
    parts = tuple(update_part(p, side, changes) if p.id == part else p for p in item.parts)
    updated = replace(item, parts=parts)
    tissue_policy.validate(updated, session.document.registry.records)
    object_operations.install(session, updated)


def update_part(part: TissuePart, side: str, changes: dict[str, Any]) -> TissuePart:
    original = getattr(part, side)
    data = asdict(original.inflation)
    data.update(changes)
    return replace(part, **{side: replace(original, inflation=tissue_codec.inflation(data))})
