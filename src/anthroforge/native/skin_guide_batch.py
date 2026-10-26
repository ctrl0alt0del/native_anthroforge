"""Pack guide sources once; native code owns identifier and path-offset assembly."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, doubles, pointer
from .skin_guides import Guides, consume


class Input(c.Structure):
    _fields_ = [
        ("samples", D),
        ("sample_count", c.c_int64),
        ("points", D),
        ("point_count", c.c_int64),
        ("offsets", INT64),
        ("path_count", c.c_int64),
    ]


def buffers(value: Guides) -> tuple[Any, Any, Any]:
    samples, points = doubles(value.samples), doubles(value.points)
    offsets = np.ascontiguousarray(value.offsets, dtype=np.int64)
    if samples.ndim != 2 or samples.shape[1] != 10:
        raise ValueError("FLOW samples require ten values per row.")
    if points.ndim != 2 or points.shape[1] != 3 or offsets.ndim != 1 or not len(offsets):
        raise ValueError("FLOW paths require XYZ points and path offsets.")
    return samples, points, offsets


def record(values: tuple[Any, Any, Any]) -> Input:
    samples, points, offsets = values
    return Input(
        pointer(samples),
        len(samples),
        pointer(points),
        len(points),
        offsets.ctypes.data_as(INT64),
        len(offsets) - 1,
    )


def merge(engine: Any, sources: tuple[Guides, ...], cancel: int = 0) -> Guides:
    owned = [buffers(value) for value in sources]
    inputs = (Input * len(owned))(*(record(value) for value in owned))
    handle = engine.library.af_skin_guides_merge(inputs, len(inputs), cancel)
    return consume(engine, handle)
