"""Cached world-space cubic queries and shape-preserving native subdivision."""

import ctypes as c
from dataclasses import replace
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve, CurvePoint

from . import construction, control_geometry, curve_editing
from .mesh import D, GeometryEngine, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_curve_closest", [D, c.c_int, D, D, D])
    engine.bind("af_curve_split", [D, c.c_int, c.c_int, c.c_int, c.c_double, D])


def cubics(engine: GeometryEngine, curve: Curve, frame: Any) -> Any:
    resolved = construction.resolved_curve(engine, curve)
    matrix = construction.matrix(engine, frame, curve.matrix)
    return control_geometry.cubics(engine, resolved, curve.closed, matrix)


class CurveQuery:
    def __init__(self, engine: GeometryEngine, curves: Any, frame: Any):
        self.engine = engine
        self.labels = [(c.id, i) for c in curves for i in range(len(c.points) - (not c.closed))]
        self.data = (
            np.concatenate([cubics(engine, curve, frame) for curve in curves])
            if curves
            else np.empty((0, 3))
        )

    def closest(self, origin: Any, direction: Any) -> dict[str, Any]:
        start, ray, output = doubles(origin), doubles(direction), np.empty(5)
        index = self.engine.library.af_curve_closest(
            pointer(self.data), len(self.labels), pointer(start), pointer(ray), pointer(output)
        )
        if index < 0:
            return {}
        curve, segment = self.labels[index]
        return dict(
            curve=curve,
            segment=segment,
            parameter=float(output[0]),
            position=output[1:4].tolist(),
            distance=float(output[4]),
        )


def split(engine: GeometryEngine, curve: Curve, segment: int, parameter: float) -> Curve:
    data, output = construction.curve_records(curve), np.empty((len(curve.points) + 1, 13))
    if curve.engine == "POLYLINE":
        data = construction.resolved_curve(engine, curve)
    engine.check(
        engine.library.af_curve_split(
            pointer(data), len(data), curve.closed, segment, parameter, pointer(output)
        )
    )
    identities = list(curve.points)
    identities.insert(segment + 1, CurvePoint())
    points = tuple(
        curve_editing.unpack(old, row) for old, row in zip(identities, output, strict=True)
    )
    return replace(curve, points=points)
