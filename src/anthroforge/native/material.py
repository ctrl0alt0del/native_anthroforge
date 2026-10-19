"""Owned native material correspondence buffers; Python only copies serialized records."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, GeometryEngine, Mesh, U


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_material_size", [U], c.c_int64)
    engine.bind("af_mesh_material_copy", [U, INT64, c.c_int64])
    engine.bind("af_mesh_with_material", [U, INT64, c.c_int64, U], U)


def array(mesh: Mesh) -> Any:
    count = mesh.engine.library.af_mesh_material_size(mesh.handle)
    mesh.engine.check(count < 0)
    output = np.empty(count, dtype=np.int64)
    mesh.engine.check(
        mesh.engine.library.af_mesh_material_copy(mesh.handle, output.ctypes.data_as(INT64), count)
    )
    return output


def restore(mesh: Mesh, values: Any, cancel: int = 0) -> Mesh:
    data = np.ascontiguousarray(values, dtype=np.int64)
    if data.ndim != 1:
        raise ValueError("Material correspondence must be a flat native record buffer.")
    if not len(data):
        return mesh
    handle = mesh.engine.library.af_mesh_with_material(
        mesh.handle, data.ctypes.data_as(INT64), len(data), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
