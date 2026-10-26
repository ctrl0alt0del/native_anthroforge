"""Owned batched adapter for the maintained native topology cross field."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, Mesh, doubles, pointer


def configure(engine: Any) -> None:
    engine.bind("af_skin_flow", [U, D, D, c.c_int, D, D, U])


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
