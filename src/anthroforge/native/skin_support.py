"""Retained anatomical samples; sampling, material resolution and weights stay native."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_fields import INT


def configure(engine: Any) -> None:
    engine.bind("af_skin_support_sample", [U, D, INT, D, D, U])
    engine.bind("af_skin_support_targets", [U, U, D, INT, c.c_int, D, U])
    engine.bind("af_skin_support_weights", [D, INT, c.c_int, D, c.c_int])
    engine.bind("af_skin_reference_replay", [D, D, c.c_int, D])


def frame(value: Any) -> Any:
    result = doubles(value)
    if result.shape != (16,):
        raise ValueError("Skin support requires sixteen world-frame values.")
    return result


def validate_replay(engine: Any, reference: Any, replay: Any) -> float:
    reference, replay = doubles(reference), doubles(replay)
    if reference.shape != replay.shape or reference.ndim != 2 or reference.shape[1] != 3:
        raise ValueError("Skin replay requires matching XYZ positions.")
    error = np.zeros(1)
    engine.check(
        engine.library.af_skin_reference_replay(
            pointer(reference), pointer(replay), len(reference), pointer(error)
        )
    )
    return float(error[0])


def sample(mesh: Any, world: Any, cancel: int = 0) -> tuple[Any, Any, float]:
    matrix = frame(world)
    ids, points, mass = np.empty(80, np.int32), np.empty((80, 3)), np.zeros(1)
    count = mesh.engine.library.af_skin_support_sample(
        mesh.handle,
        pointer(matrix),
        ids.ctypes.data_as(INT),
        pointer(points),
        pointer(mass),
        cancel,
    )
    mesh.engine.check(count < 0)
    return ids[:count], points[:count], float(mass[0])


def targets(reference: Any, current: Any, world: Any, ids: Any, cancel: int = 0) -> Any:
    matrix, ids = frame(world), np.ascontiguousarray(ids, dtype=np.int32)
    if ids.ndim != 1:
        raise ValueError("Skin sample identities must be a flat array.")
    output = np.empty((len(ids), 3))
    args = reference.handle, current.handle, pointer(matrix), ids.ctypes.data_as(INT), len(ids)
    current.engine.check(
        current.engine.library.af_skin_support_targets(*args, pointer(output), cancel)
    )
    return output


def weights(engine: Any, masses: Any, counts: Any) -> Any:
    masses, counts = doubles(masses), np.ascontiguousarray(counts, dtype=np.int32)
    if masses.ndim != 1 or counts.shape != masses.shape or np.any(counts < 1):
        raise ValueError("Skin support needs one positive count and mass per contributor.")
    output = np.empty(int(counts.sum()))
    engine.check(
        engine.library.af_skin_support_weights(
            pointer(masses), counts.ctypes.data_as(INT), len(counts), pointer(output), len(output)
        )
    )
    return output
