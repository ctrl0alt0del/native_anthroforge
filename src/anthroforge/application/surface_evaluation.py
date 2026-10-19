"""Surface evaluation consumes accepted generic paths and explicit persisted layout."""

from dataclasses import replace
from math import floor
from typing import Any

from anthroforge.core.surfaces import Surface, SurfaceAlignment
from anthroforge.native import curve_surfaces as native
from anthroforge.native import material_pins
from anthroforge.native.topology import finalize

from . import consumed_paths, curve_sources, surface_pins


def settings(item: Surface) -> native.Settings:
    return native.Settings(
        item.exact,
        item.strips,
        item.kind == "PATCH",
        item.patch_resolution,
        item.close_across,
        item.flip,
    )


def rows(
    engine: Any, document: Any, resources: Any, item: Surface, realign: bool = False
) -> list[native.Row]:
    values = item.alignment if not realign else ()
    values = values or tuple(SurfaceAlignment() for _ in item.curves)
    return [
        input_row(engine, document, resources, use, value)
        for use, value in zip(item.curves, values, strict=True)
    ]


def input_row(
    engine: Any, document: Any, resources: Any, use: Any, value: SurfaceAlignment
) -> native.Row:
    source = consumed_paths.accepted(document, resources.paths, use.curve)
    frame = curve_sources.use_frame(engine, document, use)
    indices = {point.id: i for i, point in enumerate(source.authored.points)}
    if value.point and value.point not in indices:
        raise ValueError("Surface correspondence point was removed; explicitly Realign.")
    origin = indices[value.point] + value.factor if value.point else -1
    return native.row(source.path, frame, use, origin, value.reverse)


def layout(engine: Any, document: Any, resources: Any, item: Surface, cancel: int) -> Surface:
    if item.kind == "BRANCHED":
        return replace(item, alignment=(), across=())
    values, across = native.layout(
        engine, rows(engine, document, resources, item, True), settings(item), cancel
    )
    alignment = tuple(
        stable_alignment(document, resources, use.curve, value)
        for use, value in zip(item.curves, values, strict=True)
    )
    return replace(item, alignment=alignment, across=tuple(map(int, across)))


def stable_alignment(document: Any, resources: Any, curve: str, values: Any) -> SurfaceAlignment:
    source = consumed_paths.accepted(document, resources.paths, curve)
    if not source.path.closed:
        return SurfaceAlignment()
    index = floor(float(values[0]))
    return SurfaceAlignment(
        source.authored.points[index].id, float(values[0]) - index, bool(values[1])
    )


def evaluate(engine: Any, document: Any, resources: Any, item: Surface, cancel: int) -> Any:
    from . import surface_branch_evaluation

    if item.kind == "BRANCHED":
        mesh = surface_branch_evaluation.evaluate(engine, document, resources, item, cancel)
    else:
        mesh = ordinary(engine, document, resources, item, cancel)
    previous = resources.meshes.get(item.result.asset)
    return finalize(mesh, previous.mesh if previous else None, cancel)


def ordinary(engine: Any, document: Any, resources: Any, item: Surface, cancel: int) -> Any:
    inputs = rows(engine, document, resources, item)
    counts = item.across or (max(1, item.strips) - 1,) * (len(item.curves) - 1)
    mesh = native.geometry(engine, inputs, counts, settings(item), cancel)
    pins = surface_pins.points(document, resources, [use.curve for use in item.curves])
    return material_pins.capture(mesh, inputs, pins, item.exact, cancel, across=counts)
