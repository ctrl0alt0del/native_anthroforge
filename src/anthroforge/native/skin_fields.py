"""Owned coarse skin fields. Numerical preparation stays inside the native library."""

import ctypes as c
from dataclasses import astuple
from typing import Any

import numpy as np

from anthroforge.core.skin import EnvelopeSettings

from .mesh import INT64, D, GeometryEngine, Mesh, U, pointer

BYTE = c.POINTER(c.c_uint8)
INT = c.POINTER(c.c_int)
DEFAULT_SETTINGS = EnvelopeSettings()


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_skin_fields_create", [D, c.c_int, INT64, c.c_int, BYTE, D, D, c.c_int, U, U], U)
    engine.bind("af_skin_fields_info", [U, INT, D, INT])
    engine.bind("af_skin_fields_copy", [U, c.c_int, D, U])
    engine.bind("af_skin_fields_bytes", [U], U)
    engine.bind("af_skin_fields_destroy", [U], None)
    engine.bind("af_skin_tile_mesh", [c.POINTER(c.c_float), INT, U], U)


class Fields:
    def __init__(self, engine: GeometryEngine, handle: int) -> None:
        engine.check(not handle)
        self.engine, self.handle = engine, handle
        shape, origin, resolution = (c.c_int * 3)(), (c.c_double * 4)(), c.c_int()
        engine.check(engine.library.af_skin_fields_info(handle, shape, origin, c.byref(resolution)))
        self.shape, self.origin = tuple(shape), tuple(origin[:3])
        self.voxel, self.resolution = origin[3], resolution.value
        self.bytes = int(engine.library.af_skin_fields_bytes(handle))
        if engine.resource_observer is not None:
            engine.resource_observer(self)

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_skin_fields_destroy(self.handle)
            self.handle = 0

    def array(self, kind: int) -> Any:
        output = np.empty(self.shape, dtype=np.float64)
        self.engine.check(
            self.engine.library.af_skin_fields_copy(self.handle, kind, pointer(output), output.size)
        )
        output.setflags(write=False)
        return output


def source_buffers(vertices: Any, faces: Any, skeletal: Any, collagen: Any) -> tuple[Any, ...]:
    xyz = np.ascontiguousarray(vertices, dtype=np.float64)
    indices = np.ascontiguousarray(faces, dtype=np.int64)
    scp = np.ascontiguousarray(skeletal, dtype=np.uint8)
    weights = np.ascontiguousarray(collagen, dtype=np.float64)
    if xyz.ndim != 2 or xyz.shape[1] != 3 or indices.ndim != 2 or indices.shape[1] != 3:
        raise ValueError("Skin source requires XYZ vertices and triangle indices.")
    if scp.shape != (len(indices),) or weights.shape != (len(xyz),):
        raise ValueError("Skin source membership and collagen buffers do not match geometry.")
    return xyz, indices, scp, weights


def tile_mesh(engine: GeometryEngine, values: Any, cancel: int = 0) -> Mesh:
    volume = np.ascontiguousarray(values, dtype=np.float32)
    if volume.ndim != 3:
        raise ValueError("Skin tiles require a three-dimensional scalar field.")
    shape = np.ascontiguousarray(volume.shape, dtype=np.int32)
    handle = engine.library.af_skin_tile_mesh(
        volume.ctypes.data_as(c.POINTER(c.c_float)), shape.ctypes.data_as(INT), cancel
    )
    engine.check(not handle)
    return Mesh(engine, int(handle))


def prepare(
    engine: GeometryEngine,
    vertices: Any,
    faces: Any,
    skeletal: Any,
    collagen: Any,
    settings: EnvelopeSettings = DEFAULT_SETTINGS,
    resolution: int = 220,
    budget: int = 1024**3,
    cancel: int = 0,
) -> Fields:
    buffers = source_buffers(vertices, faces, skeletal, collagen)
    return create_fields(engine, buffers, settings, resolution, budget, cancel)


def create_fields(
    engine: GeometryEngine,
    buffers: tuple[Any, ...],
    settings: EnvelopeSettings,
    resolution: int,
    budget: int,
    cancel: int,
) -> Fields:
    xyz, indices, scp, weights = buffers
    ratios = np.ascontiguousarray(astuple(settings)[:4], dtype=np.float64)
    arguments = (pointer(xyz), len(xyz), indices.ctypes.data_as(INT64), len(indices))
    fields = (scp.ctypes.data_as(BYTE), pointer(weights), pointer(ratios))
    handle = engine.library.af_skin_fields_create(*arguments, *fields, resolution, budget, cancel)
    return Fields(engine, int(handle))
