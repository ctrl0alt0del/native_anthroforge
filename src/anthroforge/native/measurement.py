"""Surface witnesses and Euclidean measurement share the native geometry boundary."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import GeometryEngine, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    d = c.POINTER(c.c_double)
    engine.bind("af_surface_point", [c.c_uint64, d, c.c_int, d, d])
    engine.bind("af_measure_points", [d, d, d])


def point(
    engine: GeometryEngine, handle: int, frame: Any, triangle: int, weights: Any
) -> tuple[float, ...]:
    matrix, bary, output = doubles(frame), doubles(weights), np.empty(3)
    if matrix.size != 16 or bary.size != 3:
        raise ValueError("Invalid surface witness dimensions.")
    configure(engine)
    engine.check(
        engine.library.af_surface_point(
            handle, pointer(matrix), triangle, pointer(bary), pointer(output)
        )
    )
    return tuple(output.tolist())


def distance(engine: GeometryEngine, first: Any, second: Any) -> list[float]:
    a, b, output = doubles(first), doubles(second), np.empty(4)
    if a.size != 3 or b.size != 3:
        raise ValueError("Measurement requires two XYZ points.")
    configure(engine)
    engine.check(engine.library.af_measure_points(pointer(a), pointer(b), pointer(output)))
    return list(output.tolist())
