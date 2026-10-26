"""Owned source-aware gap scene using the maintained addon contact predicates."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, pointer
from .skin_fields import INT

FLOAT = c.POINTER(c.c_float)


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_skin_scene_create", [D, c.c_int, INT64, c.c_int, INT, c.c_int, D, U], U)
    engine.bind("af_skin_scene_sample", [U, D, c.c_int, c.c_double, D, U])
    engine.bind("af_skin_scene_destroy", [U], None)
    engine.bind("af_skin_envelope_mesh", [U, U, U, U], U)
    engine.bind("af_skin_scene_progress", [U, INT])
    engine.bind("af_skin_scene_bind", [U, U, INT, INT, FLOAT, FLOAT, FLOAT, FLOAT, U])


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

    def envelope(self, fields: Any, budget: int = 1024**3, cancel: int = 0) -> Mesh:
        handle = self.engine.library.af_skin_envelope_mesh(
            fields.handle, self.handle, budget, cancel
        )
        self.engine.check(not handle)
        return Mesh(self.engine, int(handle))

    def progress(self) -> tuple[int, ...]:
        values = (c.c_int * 3)()
        self.engine.check(self.engine.library.af_skin_scene_progress(self.handle, values))
        return tuple(values)

    def bind(self, mesh: Mesh, cancel: int = 0) -> dict[str, Any]:
        arrays = binding_buffers(mesh.counts[0])
        pointers = [
            a.ctypes.data_as(INT if a.dtype == np.int32 else FLOAT) for a in arrays.values()
        ]
        self.engine.check(
            self.engine.library.af_skin_scene_bind(self.handle, mesh.handle, *pointers, cancel)
        )
        return arrays


def binding_buffers(count: int) -> dict[str, Any]:
    return dict(
        owners=np.empty((count, 4), dtype=np.int32),
        triangles=np.empty((count, 4), dtype=np.int32),
        barycentric=np.empty((count, 4, 3), dtype=np.float32),
        weights=np.empty((count, 4), dtype=np.float32),
        offsets=np.empty(count, dtype=np.float32),
        support=np.empty(count, dtype=np.float32),
    )


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
