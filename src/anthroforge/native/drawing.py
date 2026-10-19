"""Owned stroke fitting at the native boundary; no Qt or Python numerical fallback."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    inputs = [D, c.c_int, c.c_int, c.c_int, c.c_int, c.c_double, c.c_double]
    engine.bind(
        "af_curve_fit",
        [*inputs, c.POINTER(D), c.POINTER(c.c_int), U],
    )
    engine.bind("af_curve_fit_free", [D], None)


def fit(engine: GeometryEngine, points: Any, settings: Any, cancel: int = 0) -> Any:
    data, output, count = doubles(points), D(), c.c_int()
    if data.ndim != 2 or data.shape[1] not in (3, 4):
        raise ValueError("Drawing needs xyz or xyz/radius stroke samples.")
    args = (pointer(data), len(data), data.shape[1], settings.method_index, settings.closed)
    tail = (settings.error, settings.corner_angle, c.byref(output), c.byref(count), cancel)
    engine.check(engine.library.af_curve_fit(*args, *tail))
    try:
        return np.ctypeslib.as_array(output, shape=(count.value * 13,)).reshape((-1, 13)).copy()
    finally:
        engine.library.af_curve_fit_free(output)
