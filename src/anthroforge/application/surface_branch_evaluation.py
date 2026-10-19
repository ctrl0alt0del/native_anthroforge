"""Resolve branch membership once, then batch owned paths into native assembly."""

from typing import Any

from anthroforge.core.surfaces import SurfaceAlignment
from anthroforge.native import material_pins
from anthroforge.native import surface_branches as native

from . import consumed_paths, surface_evaluation, surface_pins


def evaluate(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> Any:
    order = (*item.main, *(key for branch in item.branches for key in branch.curves))
    uses = {u.curve: u for u in item.curves}
    rows = [
        surface_evaluation.input_row(engine, document, resources, uses[key], SurfaceAlignment())
        for key in order
    ]
    branches = [connection(document, resources, branch, order) for branch in item.branches]
    pins = surface_pins.points(document, resources, order)
    return assembled(engine, item, rows, branches, pins, cancel)


def assembled(
    engine: Any,
    item: Any,
    rows: Any,
    branches: Any,
    pins: Any,
    cancel: int,
) -> Any:
    mesh = native.geometry(
        engine, rows, len(item.main), branches, surface_evaluation.settings(item), cancel
    )
    return material_pins.capture(
        mesh, rows, pins, item.exact, cancel, main_count=len(item.main), branches=branches
    )


def connection(document: Any, resources: Any, branch: Any, order: tuple[str, ...]) -> Any:
    authored = document.object(branch.boundary)
    points = {p.junction: p.id for p in authored.points if p.junction}
    accepted = consumed_paths.accepted(document, resources.paths, branch.boundary).authored
    indices = {p.id: i for i, p in enumerate(accepted.points)}
    if any(points[key] not in indices for key in branch.junctions):
        raise ValueError(
            "Branch roots have no accepted authored correspondence; evaluate the main curve."
        )
    return native.branch(
        order.index(branch.boundary),
        [order.index(k) for k in branch.curves],
        [indices[points[key]] for key in branch.junctions],
    )
