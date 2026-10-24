"""Owned world-space presentation tubes use existing mesh publication and exact picking."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_path_display_tube", [U, D, c.c_double, c.c_int, U], U)


def tube(path: Any, matrix: Any, radius: float, sides: int = 12, cancel: int = 0) -> Mesh:
    frame = doubles(matrix)
    if frame.size != 16:
        raise ValueError("Fiber presentation requires a world transform.")
    handle = path.engine.library.af_path_display_tube(
        path.handle, pointer(frame), radius, sides, cancel
    )
    path.engine.check(not handle)
    return Mesh(path.engine, handle)
