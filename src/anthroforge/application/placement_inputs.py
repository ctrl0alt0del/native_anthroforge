"""Owned final-placement intent shared by discrete creation and fitted strokes."""

from typing import Any

import numpy as np

from anthroforge.native import strokes
from anthroforge.native.mesh import doubles

from . import surface_queries


def validated(value: Any, count: int) -> Any:
    if not value:
        return None
    queries = doubles(value["queries"]).copy()
    if queries.shape != (count, 8) or not np.isfinite(queries).all():
        raise ValueError("Placement needs one finite ray/offset/hit row per sample.")
    if not np.isin(queries[:, 7], [0, 1]).all():
        raise ValueError("Placement hit flags must be zero or one.")
    if not np.any(queries[:, 7]):
        return None
    queries.flags.writeable = False
    return dict(targets=tuple(value["targets"]), queries=queries)


def confirmed(
    engine: Any, document: Any, resources: Any, points: Any, intent: Any, cancel: int
) -> Any:
    if intent is None:
        return points
    surfaces = surface_queries.inputs(engine, document, resources.meshes, intent["targets"], cancel)
    handles, frames = surfaces
    points = doubles(points)
    if points.ndim == 2 and points.shape[1] == 3:
        points = np.column_stack((points, np.ones(len(points))))
    return strokes.confirmed(engine, handles, frames, points, intent["queries"], cancel)
