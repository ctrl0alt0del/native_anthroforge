"""Canonical connectivity restoration and reuse, independent of current vertex positions."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer, validate_arrays

INT32 = c.POINTER(c.c_int32)


def configure(engine: GeometryEngine) -> None:
    from . import material

    material.configure(engine)
    from . import tissue_inflation

    tissue_inflation.configure(engine)
    engine.bind("af_mesh_reuse_topology", [U, U, U], U)
    engine.bind("af_mesh_draft", [U, U], U)
    engine.bind("af_mesh_storage_bytes", [U], U)
    engine.bind("af_mesh_finalize", [U, U, U], U)
    engine.bind(
        "af_mesh_restore", [D, c.c_int64, INT64, INT64, c.c_int64, INT32, INT64, c.c_int64], U
    )


def restore(engine: GeometryEngine, arrays: list[Any]) -> Mesh:
    vertices = doubles(arrays[0])
    corners, offsets, polygons = (
        np.ascontiguousarray(arrays[i], dtype=np.int64) for i in (1, 2, 4)
    )
    triangles = np.ascontiguousarray(arrays[3], dtype=np.int32)
    validate_arrays(vertices, corners, offsets)
    validate_triangles(triangles, polygons, len(vertices))
    args = (pointer(vertices), len(vertices), corners.ctypes.data_as(INT64))
    tail = (offsets.ctypes.data_as(INT64), len(offsets) - 1, triangles.ctypes.data_as(INT32))
    handle = engine.library.af_mesh_restore(
        *args, *tail, polygons.ctypes.data_as(INT64), len(triangles)
    )
    engine.check(not handle)
    return Mesh(engine, handle)


def validate_triangles(triangles: Any, polygons: Any, count: int) -> None:
    if triangles.ndim != 2 or triangles.shape[1] != 3 or not len(triangles):
        raise ValueError("Invalid saved triangles.")
    if polygons.shape != (len(triangles),) or (triangles < 0).any() or (triangles >= count).any():
        raise ValueError("Invalid saved triangle references.")


def preserve(mesh: Mesh, previous: Mesh | None, cancel: int) -> Mesh:
    if previous is None:
        return mesh
    handle = mesh.engine.library.af_mesh_reuse_topology(mesh.handle, previous.handle, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def draft(mesh: Mesh, cancel: int) -> Mesh:
    handle = mesh.engine.library.af_mesh_draft(mesh.handle, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def finalize(mesh: Mesh, previous: Mesh | None, cancel: int) -> Mesh:
    handle = mesh.engine.library.af_mesh_finalize(
        mesh.handle, previous.handle if previous else 0, cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
