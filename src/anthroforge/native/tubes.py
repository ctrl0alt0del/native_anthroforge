"""Explicit world-radius tube construction shared by presentation and skin capture."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_path_tube", [U, D, c.c_double, c.c_int, U], U)


def tube(path: Any, matrix: Any, radius: float, sides: int = 12, cancel: int = 0) -> Mesh:
    frame = doubles(matrix)
    if frame.size != 16:
        raise ValueError("Tube construction requires a world transform.")
    handle = path.engine.library.af_path_tube(path.handle, pointer(frame), radius, sides, cancel)
    path.engine.check(not handle)
    return Mesh(path.engine, handle)
