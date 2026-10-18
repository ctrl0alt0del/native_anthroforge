"""Pack authored weights; C++ owns inversion and membership evaluation."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import Deformer

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_influence", [D, c.c_int, c.c_int, c.POINTER(c.c_int), c.c_int, c.c_int, D, U])


def weights(engine: GeometryEngine, binding: Deformer, count: int, cancel: int) -> Any:
    if count < 0 or (binding.weights and len(binding.weights) != count):
        raise ValueError("Influence weights do not match target points.")
    source = pointer(doubles(binding.weights)) if binding.weights else None
    if not binding.indices and not binding.restrict and (not source or not binding.invert):
        return source
    return evaluated(engine, binding, count, cancel, source)


def evaluated(
    engine: GeometryEngine, binding: Deformer, count: int, cancel: int, source: Any
) -> Any:
    indices = np.ascontiguousarray(binding.indices, dtype=np.int32)
    output = np.empty(count)
    membership = indices.ctypes.data_as(c.POINTER(c.c_int))
    args = (source, count, binding.invert, membership, len(indices), binding.restrict)
    engine.check(
        engine.library.af_influence(
            *args,
            pointer(output),
            cancel,
        )
    )
    return pointer(output)
