"""Batched bind-time owner transitions shared by anatomical point attachments."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer

INT = c.POINTER(c.c_int)


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_attachment_weights", [D, INT, c.c_int, INT, c.c_int, c.c_int, INT, D, U])


def owners(
    engine: GeometryEngine, points: Any, owners: Any, pins: Any, closed: bool, cancel: int = 0
) -> tuple[Any, Any]:
    positions = doubles(points)
    source, fixed = (np.ascontiguousarray(value, dtype=np.int32) for value in (owners, pins))
    if positions.shape != (len(source), 3) or source.ndim != 1 or fixed.ndim != 1:
        raise ValueError("Owner blending requires positions, owner IDs and fixed indices.")
    targets, weights = np.empty((len(source), 2), dtype=np.int32), np.empty((len(source), 2))
    args = (pointer(positions), source.ctypes.data_as(INT), len(source), fixed.ctypes.data_as(INT))
    engine.check(
        engine.library.af_attachment_weights(
            *args, len(fixed), closed, targets.ctypes.data_as(INT), pointer(weights), cancel
        )
    )
    return targets, weights
