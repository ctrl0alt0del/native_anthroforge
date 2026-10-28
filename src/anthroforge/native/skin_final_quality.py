"""Addon final-skin advisory queries, without retopology or geometry repair."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, U, doubles, pointer
from .skin_validation import FIELDS

CLEARANCE_FIELDS = (
    "samples",
    "negative_samples",
    "reference_negative_samples",
    "minimum",
    "maximum_clearance_loss",
    "distance_p95",
)
CLEARANCE_LIMIT = (
    "Nearest-surface normal diagnostic; not a complete skin-anatomy volume intersection check."
)


def configure(engine: Any) -> None:
    engine.bind("af_skin_intersections", [U, U, INT64, c.c_int, INT64, U])
    engine.bind("af_skin_anatomy_clearance", [U, U, D, D, c.c_int, D, U])
    engine.bind("af_skin_deformed_quality", [U, D, U])


def intersections(mesh: Any, budget: int, cancel: int = 0) -> dict[str, Any]:
    pairs, stats = np.full((256, 2), -1, np.int64), np.zeros(3, np.int64)
    args = mesh.handle, budget, pairs.ctypes.data_as(INT64), len(pairs)
    mesh.engine.check(
        mesh.engine.library.af_skin_intersections(*args, stats.ctypes.data_as(INT64), cancel)
    )
    return dict(
        self_intersections=int(stats[0]),
        contact_pairs=int(stats[1]),
        tested_pairs=int(stats[2]),
        intersection_witnesses=pairs[: min(int(stats[0]), len(pairs))].tolist(),
        intersection_tessellation="triangles; quads split on diagonal 0-2",
        intersection_check="COMPLETE",
    )


def clearance(
    reference: Any, current: Any, rest_samples: Any, samples: Any, cancel: int = 0
) -> dict[str, Any]:
    before, after = clearance_inputs(rest_samples, samples)
    result = np.zeros(6)
    args = reference.handle, current.handle, pointer(before), pointer(after), len(before)
    reference.engine.check(
        reference.engine.library.af_skin_anatomy_clearance(*args, pointer(result), cancel)
    )
    return dict(zip(CLEARANCE_FIELDS, result.tolist(), strict=True)) | dict(
        interpretation=CLEARANCE_LIMIT
    )


def clearance_inputs(rest_samples: Any, samples: Any) -> tuple[Any, Any]:
    before, after = doubles(rest_samples), doubles(samples)
    if (
        before.ndim != 2
        or before.shape[1:] != (3,)
        or before.shape != after.shape
        or not len(before)
    ):
        raise ValueError("Skin clearance requires matching reference and current XYZ samples.")
    return before, after


def topology(mesh: Any, cancel: int = 0) -> dict[str, Any]:
    result = np.zeros(16)
    mesh.engine.check(
        mesh.engine.library.af_skin_deformed_quality(mesh.handle, pointer(result), cancel)
    )
    retained = (0, 1, 2, 3, 4, 5, 6, 13, 14, 15)
    return {FIELDS[i]: float(result[i]) for i in retained}
