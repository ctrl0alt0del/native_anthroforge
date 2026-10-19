"""Validated native tissue material maps and labels; opaque to Python numerical code."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_tissue_sizes", [U, INT64])
    engine.bind("af_mesh_tissue_copy", [U, INT64, c.c_int64, D, c.c_int64])
    engine.bind("af_mesh_tissue_restore", [U, INT64, c.c_int64, D, c.c_int64, U], U)


def arrays(mesh: Mesh) -> tuple[Any, Any]:
    sizes = (c.c_int64 * 2)()
    mesh.engine.check(mesh.engine.library.af_mesh_tissue_sizes(mesh.handle, sizes))
    records, weights = np.empty(sizes[0], dtype=np.int64), np.empty(sizes[1])
    mesh.engine.check(
        mesh.engine.library.af_mesh_tissue_copy(
            mesh.handle, records.ctypes.data_as(INT64), sizes[0], pointer(weights), sizes[1]
        )
    )
    return records, weights


def restore(mesh: Mesh, records: Any, weights: Any, cancel: int = 0) -> Mesh:
    data, values = np.ascontiguousarray(records, dtype=np.int64), doubles(weights)
    if data.ndim != 1 or values.ndim != 1:
        raise ValueError("Tissue domain requires flat native record buffers.")
    if not len(data) and not len(values):
        return mesh
    handle = mesh.engine.library.af_mesh_tissue_restore(
        mesh.handle, data.ctypes.data_as(INT64), len(data), pointer(values), len(values), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
