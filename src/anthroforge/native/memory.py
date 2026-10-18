"""Bounded native allocation inventory, queried only by an active recorder."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import GeometryEngine


def snapshot(engine: GeometryEngine, limit: int = 4096) -> tuple[list[Any], int]:
    rows, total = np.empty((limit, 7), dtype=np.uint64), c.c_uint64()
    pointer = c.POINTER(c.c_uint64)
    engine.bind("af_mesh_memory_snapshot", [pointer, c.c_int, pointer])
    count = engine.library.af_mesh_memory_snapshot(
        rows.ctypes.data_as(pointer), limit, c.byref(total)
    )
    if count < 0:
        raise ValueError("Native memory inventory failed.")
    return rows[:count].tolist(), total.value


def path_snapshot(engine: GeometryEngine, limit: int = 4096) -> tuple[list[Any], int]:
    rows, total = np.empty((limit, 3), dtype=np.uint64), c.c_uint64()
    pointer = c.POINTER(c.c_uint64)
    engine.bind("af_path_memory_snapshot", [pointer, c.c_int, pointer])
    count = engine.library.af_path_memory_snapshot(
        rows.ctypes.data_as(pointer), limit, c.byref(total)
    )
    if count < 0:
        raise ValueError("Native path memory inventory failed.")
    return rows[:count].tolist(), total.value
