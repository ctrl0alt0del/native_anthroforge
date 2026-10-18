"""Batched native display-line and query-control preparation."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_polyline_lines", [D, c.c_int, c.c_int, c.c_int, D, D])
    engine.bind("af_lattice_lines", [D, c.c_int, c.POINTER(c.c_int), D, D])
    engine.bind("af_curve_cubics", [D, c.c_int, c.c_int, D, D])


def polylines(
    engine: GeometryEngine, points: Any, matrix: Any, closed: bool = False, group: int = 0
) -> Any:
    data, frame = doubles(points).reshape((-1, 3)), doubles(matrix)
    output = np.empty((2 * len(data), 3))
    args = (pointer(data), len(data), group or max(1, len(data)), closed)
    count = engine.library.af_polyline_lines(*args, pointer(frame), pointer(output))
    engine.check(count < 0)
    return output[:count]


def cage_lines(engine: GeometryEngine, points: Any, resolution: Any, matrix: Any) -> Any:
    data, frame = doubles(points).reshape((-1, 3)), doubles(matrix)
    if len(resolution) != 3:
        raise ValueError("Lattice resolution requires three dimensions.")
    output = np.empty((6 * len(data), 3))
    count = engine.library.af_lattice_lines(
        pointer(data), len(data), (c.c_int * 3)(*resolution), pointer(frame), pointer(output)
    )
    engine.check(count < 0)
    return output[:count]


def cubics(engine: GeometryEngine, records: Any, closed: bool, matrix: Any) -> Any:
    data, frame = doubles(records).reshape((-1, 13)), doubles(matrix)
    output = np.empty((max(0, len(data) - (not closed)) * 4, 3))
    engine.check(
        engine.library.af_curve_cubics(
            pointer(data), len(data), closed, pointer(frame), pointer(output)
        )
    )
    return output
