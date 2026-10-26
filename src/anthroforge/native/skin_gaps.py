"""Owned source-aware gap scene using the maintained addon contact predicates."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, U, pointer
from .skin_fields import INT


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_skin_scene_create", [D, c.c_int, INT64, c.c_int, INT, c.c_int, D, U], U)
    engine.bind("af_skin_scene_sample", [U, D, c.c_int, c.c_double, D, U])
    engine.bind("af_skin_scene_destroy", [U], None)


class Scene:
    def __init__(self, engine: GeometryEngine, handle: int) -> None:
        engine.check(not handle)
        self.engine, self.handle = engine, handle

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_skin_scene_destroy(self.handle)
            self.handle = 0

    def sample(self, points: Any, reach: float, cancel: int = 0) -> Any:
        values = np.ascontiguousarray(points, dtype=np.float64)
        if values.ndim != 2 or values.shape[1] != 3:
            raise ValueError("Skin gap queries require XYZ positions.")
        output = np.empty((len(values), 13), dtype=np.float64)
        self.engine.check(
            self.engine.library.af_skin_scene_sample(
                self.handle, pointer(values), len(values), reach, pointer(output), cancel
            )
        )
        return output


def buffers(vertices: Any, faces: Any, owners: Any, policies: Any) -> tuple[Any, ...]:
    xyz, rules = (np.ascontiguousarray(v, dtype=np.float64) for v in (vertices, policies))
    triangles = np.ascontiguousarray(faces, dtype=np.int64)
    membership = np.ascontiguousarray(owners, dtype=np.int32)
    if any(v.ndim != 2 or v.shape[1] != 3 for v in (xyz, triangles, rules)):
        raise ValueError("Skin source requires XYZ vertices, triangles and three-column policies.")
    if membership.shape != (len(triangles),):
        raise ValueError("Skin source ownership must match triangle count.")
    return xyz, triangles, membership, rules


def create(
    engine: GeometryEngine, vertices: Any, faces: Any, owners: Any, policies: Any, cancel: int = 0
) -> Scene:
    xyz, triangles, membership, rules = buffers(vertices, faces, owners, policies)
    geometry = (pointer(xyz), len(xyz), triangles.ctypes.data_as(INT64), len(triangles))
    source = (membership.ctypes.data_as(INT), len(rules), pointer(rules), cancel)
    return Scene(engine, int(engine.library.af_skin_scene_create(*geometry, *source)))
