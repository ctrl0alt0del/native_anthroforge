"""Mirrored rows build one source surface, retaining explicit material row ordering."""

from dataclasses import replace
from typing import Any

from anthroforge.core.entities import IDENTITY
from anthroforge.core.surfaces import Surface
from anthroforge.native import construction, curve_surfaces

from . import curve_sources, symmetric_paths


def reflection(engine: Any, document: Any, item: Any) -> Any:
    world = (
        curve_sources.world(engine, document, item.id)
        if item.id in document.registry.records
        else placed(engine, document, item)
    )
    plane = symmetric_paths.plane(document, item.mirror_plane)
    return construction.matrix(engine, world, construction.matrix(engine, plane.frame, world), True)


def placed(engine: Any, document: Any, item: Any) -> Any:
    return construction.matrix(
        engine, curve_sources.world(engine, document, item.parent), item.matrix
    )


def expand(engine: Any, document: Any, item: Any, rows: Any) -> Any:
    if not item.mirrored_rows:
        return rows
    if not item.mirror_order:
        raise ValueError("Mirrored rows need a captured layout; use Realign.")
    frame = reflection(engine, document, item)
    return [
        row(engine, rows[abs(index) - 1], frame if index < 0 else IDENTITY)
        for index in item.mirror_order
    ]


def row(engine: Any, source: Any, frame: Any) -> Any:
    result = curve_surfaces.Row.from_buffer_copy(bytes(source))
    result.matrix[:] = construction.matrix(engine, frame, tuple(source.matrix))
    result._source_owner = source
    return result


def layout(
    engine: Any, document: Any, resources: Any, item: Surface, rows: Any, cancel: int
) -> Surface:
    from .surface_evaluation import settings

    if not item.mirrored_rows:
        return item
    plane = symmetric_paths.plane(document, item.mirror_plane)
    world = placed(engine, document, item)
    order = curve_surfaces.mirror_order(engine, rows, world, plane, cancel)
    candidate = replace(item, mirror_order=order, across=())
    expanded = expand(engine, document, candidate, rows)
    _, across = curve_surfaces.layout(engine, expanded, settings(candidate), cancel)
    return replace(candidate, across=tuple(map(int, across)))


def pins(item: Any, points: Any) -> Any:
    if not item.mirrored_rows:
        return points
    grouped: dict[int, list[int]] = {}
    for source, point in points:
        grouped.setdefault(source, []).append(point)
    return [
        (row, point)
        for row, source in enumerate(item.mirror_order)
        for point in grouped.get(abs(source) - 1, ())
    ]
