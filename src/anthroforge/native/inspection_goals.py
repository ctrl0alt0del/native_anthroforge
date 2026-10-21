"""Native material-interpolated constraint goals and displayed-result residuals."""

import ctypes as c
from typing import Any

import numpy as np

from . import tissue_relaxation as relaxation
from .mesh import D, U, doubles, pointer


def configure(engine: Any) -> None:
    source, region = c.POINTER(relaxation.Source), c.POINTER(relaxation.Region)
    engine.bind("af_inspection_goals", [U, U, source, c.c_int, D, D, region, c.c_int, D, U])


def sample(
    mesh: Any, rest: Any, source: Any, item: Any, goals: Any, query: Any, cancel: int
) -> Any:
    triangle, bary, frame = query
    weights, matrix = doubles(bary), doubles(frame)
    relaxation.validate_goals(rest, goals)
    if weights.shape != (3,) or matrix.size != 16:
        raise ValueError("Constraint inspection requires triangle weights and a world frame.")
    rows, leases = relaxation.regions(item, goals)
    result = np.zeros((len(rows), 7))
    args = mesh.handle, rest.handle, c.byref(source), triangle, pointer(weights), pointer(matrix)
    mesh.engine.check(
        mesh.engine.library.af_inspection_goals(*args, rows, len(rows), pointer(result), cancel)
    )
    return result.tolist()
