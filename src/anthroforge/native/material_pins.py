"""Capture and serialize exact structural material locations without Python geometry queries."""

import ctypes as c
from typing import Any

import numpy as np

from .curve_surfaces import INT, Row
from .mesh import D, Mesh, U, pointer
from .surface_branches import Branch
from .tissue_shapes import owned


class Inputs(c.Structure):
    _fields_ = [("rows", c.POINTER(Row))]
    _fields_ += [(name, c.c_int) for name in ("count", "exact", "main_count")]
    _fields_ += [("across", INT), ("branches", c.POINTER(Branch)), ("branch_count", c.c_int)]
    _fields_ += [("points", INT), ("point_count", c.c_int)]


def configure(engine: Any) -> None:
    engine.bind("af_surface_material_pins", [U, c.POINTER(Inputs), U], U)
    engine.bind("af_mesh_material_pins", [U, D, c.c_int64], c.c_int64)
    engine.bind("af_mesh_with_material_pins", [U, D, c.c_int64, U], U)


def array(mesh: Mesh) -> Any:
    method = mesh.engine.library.af_mesh_material_pins
    count = method(mesh.handle, None, 0)
    mesh.engine.check(count < 0)
    data = np.empty(count, dtype=np.float64)
    mesh.engine.check(method(mesh.handle, pointer(data), count) < 0)
    return data.reshape((-1, 11))


def restore(mesh: Mesh, data: Any, cancel: int = 0) -> Mesh:
    values = np.ascontiguousarray(data, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 11:
        raise ValueError("Retained material pins require eleven values per record.")
    if not len(values):
        return mesh
    handle = mesh.engine.library.af_mesh_with_material_pins(
        mesh.handle, pointer(values), values.size, cancel
    )
    return owned(mesh.engine, handle)


def capture(
    mesh: Mesh, rows: Any, points: Any, exact: bool, cancel: int = 0, **layout: Any
) -> Mesh:
    if not points:
        return mesh
    config, _buffers = packed(rows, points, exact, **layout)
    handle = mesh.engine.library.af_surface_material_pins(mesh.handle, c.byref(config), cancel)
    return owned(mesh.engine, handle)


def packed(rows: Any, points: Any, exact: bool, **layout: Any) -> tuple[Inputs, tuple[Any, ...]]:
    sources = (Row * len(rows))(*rows)
    branches = layout.get("branches", ())
    branch_rows = (Branch * len(branches))(*branches)
    across = np.ascontiguousarray(layout.get("across", ()), dtype=np.int32)
    pins = np.ascontiguousarray(points, dtype=np.int32).reshape((-1, 2))
    config = Inputs(sources, len(sources), exact, layout.get("main_count", 0))
    config.across = across.ctypes.data_as(INT)
    config.branches, config.branch_count = branch_rows, len(branch_rows)
    config.points, config.point_count = pins.ctypes.data_as(INT), len(pins)
    return config, (sources, branch_rows, across, pins)
