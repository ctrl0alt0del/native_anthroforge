"""Qualified sample containment is not a proof of whole-surface containment or MTV depth."""

import ctypes as c
from typing import Any

import numpy as np

from .inspection_metrics import array
from .mesh import INT64, D, U, pointer

REASONS = {
    1: "Open or invalid volume",
    3: "Invalid or nonmanifold topology",
    4: "Self-intersecting volume",
    5: "Nested interior shells",
    6: "Inconsistent orientation",
}


def configure(engine: Any) -> None:
    engine.bind("af_inspection_volume", [U, D, U, D, c.c_int, D, INT64, U])


def inspect(source: Any, frame: Any, volume: Any, other: Any, cancel: int) -> dict[str, Any]:
    a, b, rows = array(frame, 16), array(other, 16), np.empty((512, 8))
    counts = np.zeros(5, dtype=np.int64)
    code = source.engine.library.af_inspection_volume(
        source.handle,
        pointer(a),
        volume.handle,
        pointer(b),
        len(rows),
        pointer(rows),
        counts.ctypes.data_as(INT64),
        cancel,
    )
    source.engine.check(code < 0)
    return report(source, rows, counts, code)


def report(source: Any, rows: Any, counts: Any, code: int) -> dict[str, Any]:
    inside = rows[counts[4]] if code == 0 and counts[4] >= 0 else None
    return dict(
        available=code == 0,
        reason=REASONS.get(code, "") if code else "",
        samples=rows[: counts[0]].tolist() if code == 0 else [],
        sampled=int(counts[0]),
        vertices=source.counts[0],
        inside=int(counts[1]),
        boundary=int(counts[2]),
        outside=int(counts[3]),
        maximum_inside_distance=float(inside[1]) if inside is not None else 0,
        lines=inside[2:].reshape((2, 3)).tolist() if inside is not None else [],
        **method(),
    )


def method() -> dict[str, str]:
    return dict(
        units="metres",
        method="CGAL closed exterior volume; deterministic vertex samples",
        limitation="Samples do not certify whole-surface containment or a separating translation.",
    )
