"""Owned batched adapter for the maintained native topology cross field."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, Mesh, U, doubles, pointer


def configure(engine: Any) -> None:
    engine.bind("af_skin_flow", [U, D, D, c.c_int, D, D, U])
    integers = c.POINTER(c.c_int)
    engine.bind("af_skin_flow_route", [U, D, c.c_int, integers, c.c_int, U])
    engine.bind("af_skin_flow_select", [U, D, c.c_int, integers, c.c_int, integers, U])


def solve(mesh: Mesh, prior: Any, samples: Any, cancel: int = 0) -> tuple[Any, Any]:
    directions, values = doubles(prior), doubles(samples)
    validate(mesh, directions, values)
    output, information = np.empty_like(directions), np.empty_like(directions)
    inputs = mesh.handle, pointer(directions), pointer(values), len(values)
    outputs = pointer(output), pointer(information), cancel
    mesh.engine.check(mesh.engine.library.af_skin_flow(*inputs, *outputs))
    return output, information


def validate(mesh: Mesh, directions: Any, values: Any) -> None:
    if directions.shape != (mesh.counts[3], 3):
        raise ValueError("FLOW prior needs one XYZ direction per triangle.")
    if values.ndim != 2 or values.shape[1] != 10:
        raise ValueError("FLOW samples need position, direction, normal and owner.")


def route(mesh: Mesh, points: Any, cancel: int = 0) -> Any:
    values = path_points(points)
    output = np.empty(mesh.counts[3] * 6, dtype=np.int32)
    count = mesh.engine.library.af_skin_flow_route(
        mesh.handle, pointer(values), len(values), integers(output), len(output), cancel
    )
    mesh.engine.check(count < 0)
    return output[: count * 2].reshape(-1, 2)


def select_paths(mesh: Mesh, points: Any, offsets: Any, cancel: int = 0) -> Any:
    values, ranges = path_points(points), np.ascontiguousarray(offsets, dtype=np.int32)
    if ranges.ndim != 1 or len(ranges) < 2:
        raise ValueError("FLOW paths need start and end offsets.")
    output = np.empty(len(ranges) - 1, dtype=np.int32)
    inputs = mesh.handle, pointer(values), len(values), integers(ranges), len(output)
    count = mesh.engine.library.af_skin_flow_select(*inputs, integers(output), cancel)
    mesh.engine.check(count < 0)
    return output[:count]


def integers(values: Any) -> Any:
    return values.ctypes.data_as(c.POINTER(c.c_int))


def path_points(points: Any) -> Any:
    values = doubles(points)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("FLOW paths need XYZ points.")
    return values
