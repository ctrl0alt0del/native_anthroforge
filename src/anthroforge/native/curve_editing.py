"""Native handle-aware edits shared by inspector and viewport operations."""

import ctypes as c
from dataclasses import replace
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve, CurvePoint

from .construction import HANDLES, curve_records
from .mesh import D, GeometryEngine, pointer

FIELDS = ("position", "left", "right", "left_mode", "right_mode", "radius", "tilt")


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_curve_point_edit", [D, c.c_int, c.c_int, c.c_int, D, c.c_int, D])


def point(engine: GeometryEngine, curve: Curve, index: int, options: dict[str, Any]) -> CurvePoint:
    if set(options) - set(FIELDS):
        raise ValueError("Unknown curve-point setting.")
    old = curve.points[index]
    updated = replace(old, **options)
    data, output = curve_records(curve), np.empty(13)
    points = tuple(updated if i == index else p for i, p in enumerate(curve.points))
    replacement = curve_records(replace(curve, points=points))[index]
    fields = sum(1 << bit for bit, name in enumerate(FIELDS) if name in options)
    apply_edit(engine, data, curve.closed, index, replacement, fields, output)
    return unpack(old, output)


def apply_edit(
    engine: GeometryEngine,
    data: Any,
    closed: bool,
    index: int,
    replacement: Any,
    fields: int,
    output: Any,
) -> None:
    args = (pointer(data), len(data), closed, index, pointer(replacement), fields, pointer(output))
    engine.check(engine.library.af_curve_point_edit(*args))


def unpack(old: CurvePoint, record: Any) -> CurvePoint:
    return replace(
        old,
        position=tuple(record[:3]),
        left=tuple(record[3:6]),
        right=tuple(record[6:9]),
        radius=float(record[9]),
        tilt=float(record[10]),
        left_mode=HANDLES[int(record[11])],
        right_mode=HANDLES[int(record[12])],
    )
