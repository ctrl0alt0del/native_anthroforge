"""Batched advisory collision checks on immutable accepted paths; no Python geometry loops."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer

INT = c.POINTER(c.c_int)


class CollisionPath(c.Structure):
    _fields_ = [("path", U), ("world", c.c_double * 16), ("count", c.c_int), ("owners", INT)]


def configure(engine: GeometryEngine) -> None:
    engine.bind(
        "af_path_collisions",
        [c.POINTER(CollisionPath), c.c_int, c.POINTER(U), D, c.c_int, INT, D, U],
    )


def row(path: Any, world: Any, owners: Any) -> CollisionPath:
    data = np.asarray(owners, dtype=np.int32)
    if data.ndim != 1 or len(world) != 16:
        raise ValueError("Collision path needs a frame and one owner per authored knot.")
    result = CollisionPath(
        path.handle, (c.c_double * 16)(*world), len(data), data.ctypes.data_as(INT)
    )
    result._leases = (path, data)
    return result


def check(
    engine: GeometryEngine, rows: list[CollisionPath], handles: Any, frames: Any, cancel: int = 0
) -> Any:
    meshes, frames = np.asarray(handles, dtype=np.uint64), doubles(frames)
    if frames.size != len(meshes) * 16 or len(rows) * len(meshes) > 1000000:
        raise ValueError("Invalid collision surface frames or excessive pair count.")
    return invoke(engine, rows, meshes, frames, cancel)


def invoke(engine: GeometryEngine, rows: Any, meshes: Any, frames: Any, cancel: int) -> Any:
    output, tolerance = np.empty((len(rows), len(meshes)), dtype=np.int32), np.empty(1)
    engine.check(
        engine.library.af_path_collisions(
            (CollisionPath * len(rows))(*rows),
            len(rows),
            meshes.ctypes.data_as(c.POINTER(U)),
            pointer(frames),
            len(meshes),
            output.ctypes.data_as(INT),
            pointer(tolerance),
            cancel,
        )
    )
    return output, float(tolerance[0])
