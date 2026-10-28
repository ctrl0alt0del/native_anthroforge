"""Native proximity density adjustment and coarse-mesh target calculation."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from . import skin_ownership
from .mesh import D, U, pointer
from .skin_fields import BYTE, INT


@dataclass(frozen=True)
class Result:
    lengths: Any
    weights: Any
    statistics: Any


def configure(engine: Any) -> None:
    engine.bind("af_skin_proximity", [U, c.POINTER(skin_ownership.Input), BYTE, D, D, D, D, U])
    engine.bind("af_skin_base_target", [U, D, c.c_int, c.c_int, INT, U])


def evaluate(mesh: Any, data: Any, enabled: Any, lengths: Any, cancel: int = 0) -> Result:
    request = skin_ownership.request(data)
    mask, values = (
        np.ascontiguousarray(enabled, dtype=np.uint8),
        np.ascontiguousarray(lengths, dtype=np.float64),
    )
    if mask.shape != (request.source_count,) or values.shape != (mesh.counts[0],):
        raise ValueError("Proximity needs one flag per source and one length per skin vertex.")
    return run(mesh, request, mask, values, cancel)


def run(mesh: Any, request: Any, mask: Any, values: Any, cancel: int) -> Result:
    output, weights, stats = np.empty_like(values), np.empty_like(values), np.empty(5)
    args = mesh.handle, c.byref(request), mask.ctypes.data_as(BYTE), pointer(values)
    mesh.engine.check(
        mesh.engine.library.af_skin_proximity(
            *args, pointer(output), pointer(weights), pointer(stats), cancel
        )
    )
    return Result(output, weights, stats)


def base_target(mesh: Any, lengths: Any, target: int, reserved: int = 0, cancel: int = 0) -> int:
    values = np.ascontiguousarray(lengths, dtype=np.float64)
    if values.shape != (mesh.counts[0],):
        raise ValueError("Topology target needs one length per source vertex.")
    output = c.c_int()
    mesh.engine.check(
        mesh.engine.library.af_skin_base_target(
            mesh.handle, pointer(values), target, reserved, c.byref(output), cancel
        )
    )
    return output.value
