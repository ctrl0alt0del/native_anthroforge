"""Batched placement witnesses over the production preview and confirmed query meshes."""

import ctypes as c
from typing import Any

import numpy as np

from .inspection_metrics import array
from .mesh import D, U, pointer
from .point_attachments import surface_arrays


def configure(engine: Any) -> None:
    engine.bind("af_inspection_placement", [c.c_int, c.POINTER(U), D, D, c.c_int, D, U])


def inspect(engine: Any, handles: Any, frames: Any, request: Any, ray: bool, cancel: int) -> Any:
    meshes, world = surface_arrays(handles, frames)
    data, rows = array(request, 7), np.empty((len(meshes), 16))
    args = len(meshes), meshes.ctypes.data_as(c.POINTER(U)), pointer(world), pointer(data)
    winner = engine.library.af_inspection_placement(*args, ray, pointer(rows), cancel)
    engine.check(winner < -1)
    return dict(winner=winner, candidates=[record(row) for row in rows])


def record(row: Any) -> dict[str, Any]:
    return dict(
        hit=row[0] >= 0,
        triangle=int(row[0]),
        distance=row[1],
        position=row[2:5].tolist(),
        normal=row[5:8].tolist(),
        accepted=row[8:11].tolist(),
        signed_normal_distance=row[11],
        approach_cosine=row[12],
        query_triangle=int(row[13]),
        qualified_copy=bool(row[14]),
        requested_distance=row[15],
    )
