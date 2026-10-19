"""Owned native material correspondence buffers; Python only copies serialized records."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_material_size", [U], c.c_int64)
    engine.bind("af_mesh_material_copy", [U, INT64, c.c_int64])
    engine.bind("af_mesh_with_material", [U, INT64, c.c_int64, D, c.c_int64, U], U)
    engine.bind("af_mesh_material_axes", [U, D, c.c_int64], c.c_int64)


def array(mesh: Mesh) -> Any:
    count = mesh.engine.library.af_mesh_material_size(mesh.handle)
    mesh.engine.check(count < 0)
    output = np.empty(count, dtype=np.int64)
    mesh.engine.check(
        mesh.engine.library.af_mesh_material_copy(mesh.handle, output.ctypes.data_as(INT64), count)
    )
    return output


def axes(mesh: Mesh) -> Any:
    method = mesh.engine.library.af_mesh_material_axes
    count = method(mesh.handle, None, 0)
    mesh.engine.check(count < 0)
    result = np.empty(count, dtype=np.float64)
    mesh.engine.check(method(mesh.handle, pointer(result), count) < 0)
    return result


def restore(mesh: Mesh, values: Any, cancel: int = 0, parameters: Any = ()) -> Mesh:
    data = np.ascontiguousarray(values, dtype=np.int64)
    coordinates = np.ascontiguousarray(parameters, dtype=np.float64)
    if data.ndim != 1 or coordinates.ndim != 1:
        raise ValueError("Material correspondence must be a flat native record buffer.")
    if not len(data) and not len(coordinates):
        return mesh
    return install(mesh, data, coordinates, cancel)


def install(mesh: Mesh, data: Any, coordinates: Any, cancel: int) -> Mesh:
    handle = mesh.engine.library.af_mesh_with_material(
        mesh.handle,
        data.ctypes.data_as(INT64),
        len(data),
        pointer(coordinates),
        len(coordinates),
        cancel,
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
