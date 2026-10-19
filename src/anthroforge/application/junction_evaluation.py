"""Resolve explicit shared points from accepted source paths before invoking an engine."""

from dataclasses import replace
from typing import Any

from anthroforge.core.junctions import PointRef
from anthroforge.native import construction, curve_editing, path_editing

from . import consumed_paths, curve_sources
from .path_assets import PathAsset


def resolved(
    engine: Any, document: Any, resources: Any, item: Any, cancel: int, path: Any = None
) -> Any:
    changed = definition(engine, document, resources, item)
    if changed == item:
        return item, path
    if path is None or item.engine == "ROUTED":
        return changed, replace(path, authored=changed) if path else None
    updated, records = path_editing.rebase(path.path, item, changed, cancel)
    points = tuple(
        curve_editing.unpack(p, row) for p, row in zip(changed.points, records, strict=True)
    )
    changed = replace(changed, points=points)
    return changed, PathAsset(updated, changed)


def definition(engine: Any, document: Any, resources: Any, item: Any) -> Any:
    if not document.junctions:
        return item
    links = {j.id: j for j in document.junctions}
    changed = item
    for i, point in enumerate(item.points):
        junction = links.get(point.junction)
        if junction and junction.source != PointRef(item.id, point.id):
            position = source_position(engine, document, resources, item.id, junction.source)
            value = curve_editing.point(engine, changed, i, dict(position=position))
            changed = replace(
                changed, points=tuple(value if p.id == point.id else p for p in changed.points)
            )
    return changed


def source_position(engine: Any, document: Any, resources: Any, target: str, ref: PointRef) -> Any:
    asset = consumed_paths.accepted(document, resources.paths, ref.curve)
    point = next((p for p in asset.authored.points if p.id == ref.point), None)
    if point is None:
        raise ValueError("Junction source has no accepted authored point.")
    source = curve_sources.world(engine, document, ref.curve)
    target_frame = curve_sources.world(engine, document, target)
    relative = construction.matrix(engine, target_frame, source, relative=True)
    return engine.world_point(relative, point.position)
