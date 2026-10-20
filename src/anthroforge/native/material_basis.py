"""Self-contained source material coordinates retained by accepted geometry."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_basis_sizes", [U, INT64])
    engine.bind("af_mesh_basis_copy", [U, INT64, c.c_int64, D, c.c_int64])
    engine.bind("af_mesh_basis_restore", [U, INT64, c.c_int64, D, c.c_int64, U], U)


def arrays(mesh: Mesh) -> tuple[Any, Any]:
    sizes = (c.c_int64 * 2)()
    mesh.engine.check(mesh.engine.library.af_mesh_basis_sizes(mesh.handle, sizes))
    records, parameters = np.empty(sizes[0], dtype=np.int64), np.empty(sizes[1])
    mesh.engine.check(
        mesh.engine.library.af_mesh_basis_copy(
            mesh.handle, records.ctypes.data_as(INT64), sizes[0], pointer(parameters), sizes[1]
        )
    )
    return records, parameters


def restore(mesh: Mesh, records: Any, parameters: Any, cancel: int = 0) -> Mesh:
    data, values = np.ascontiguousarray(records, dtype=np.int64), doubles(parameters)
    if data.ndim != 1 or values.ndim != 1:
        raise ValueError("Material basis needs flat record buffers.")
    if not len(data) and not len(values):
        return mesh
    handle = mesh.engine.library.af_mesh_basis_restore(
        mesh.handle, data.ctypes.data_as(INT64), len(data), pointer(values), len(values), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
