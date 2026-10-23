"""Persistent per-triangle source provenance for topology-changing construction."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_triangle_material_sizes", [U, INT64])
    engine.bind("af_mesh_triangle_material_copy", [U, INT64, c.c_int64, D, c.c_int64])
    engine.bind("af_mesh_triangle_material_restore", [U, INT64, c.c_int64, D, c.c_int64, U], U)
    engine.bind("af_mesh_triangle_source_size", [U], c.c_int64)
    engine.bind("af_mesh_triangle_source_copy", [U, D, c.c_int64])
    engine.bind("af_mesh_triangle_source_restore", [U, D, c.c_int64, U], U)


def arrays(mesh: Mesh) -> tuple[Any, Any]:
    sizes = (c.c_int64 * 2)()
    mesh.engine.check(mesh.engine.library.af_mesh_triangle_material_sizes(mesh.handle, sizes))
    records, coordinates = np.empty(sizes[0], dtype=np.int64), np.empty(sizes[1])
    mesh.engine.check(
        mesh.engine.library.af_mesh_triangle_material_copy(
            mesh.handle, records.ctypes.data_as(INT64), sizes[0], pointer(coordinates), sizes[1]
        )
    )
    return records, coordinates


def restore(mesh: Mesh, records: Any, coordinates: Any, cancel: int = 0) -> Mesh:
    data, values = np.ascontiguousarray(records, dtype=np.int64), doubles(coordinates)
    if data.ndim != 1 or values.ndim != 1:
        raise ValueError("Triangle material requires flat record buffers.")
    if not len(data) and not len(values):
        return mesh
    handle = mesh.engine.library.af_mesh_triangle_material_restore(
        mesh.handle, data.ctypes.data_as(INT64), len(data), pointer(values), len(values), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def source(mesh: Mesh) -> Any:
    count = mesh.engine.library.af_mesh_triangle_source_size(mesh.handle)
    mesh.engine.check(count < 0)
    values = np.empty(count)
    mesh.engine.check(
        mesh.engine.library.af_mesh_triangle_source_copy(mesh.handle, pointer(values), count)
    )
    return values


def restore_source(mesh: Mesh, values: Any, cancel: int = 0) -> Mesh:
    data = doubles(values)
    if data.ndim != 1:
        raise ValueError("Boolean construction chart requires a flat buffer.")
    if not len(data):
        return mesh
    handle = mesh.engine.library.af_mesh_triangle_source_restore(
        mesh.handle, pointer(data), len(data), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
