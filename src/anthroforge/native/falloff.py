"""Blender CurveMapping tables prepared once per native Hook batch."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import Deformer

from .mesh import D, GeometryEngine, doubles, pointer

MODES = ("AUTO", "VECTOR", "AUTO_CLAMPED")


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_curve_mapping", [D, c.POINTER(c.c_int), c.c_int, c.c_int, D])


def table(engine: GeometryEngine, binding: Deformer) -> Any:
    points = doubles(binding.custom)
    if binding.falloff != "CURVE":
        return points
    count = len(points) // 2
    names = binding.custom_handles or ("AUTO",) * count
    modes = (c.c_int * count)(*(MODES.index(name) for name in names))
    output = np.empty(514)
    args = (pointer(points), modes, count, binding.custom_extrapolate, pointer(output))
    engine.check(engine.library.af_curve_mapping(*args))
    return output
