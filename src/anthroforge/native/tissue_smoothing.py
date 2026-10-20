"""Batch full material sides through the qualified constrained height solver."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.tissue_diagnostics import TissueDiagnostic

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer
from .tissue_shapes import owned


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_tissue_smooth_diagnostics", [U, U, D, c.c_int, D, U], U)


def settings(side: Any) -> tuple[float, ...]:
    s = side.smoothing
    active = side.inflation.enabled and s.mode == "HEIGHT"
    return float(active), s.radius, s.strength, s.maximum_change


def evaluate(base: Mesh, own: Mesh, parts: Any, side: str, cancel: int = 0) -> Any:
    values = [settings(getattr(part, side)) for part in parts]
    if not any(all(row) for row in values):
        return own, ()
    packed, reports = doubles(values), np.zeros((len(parts), 13))
    handle = own.engine.library.af_tissue_smooth_diagnostics(
        base.handle, own.handle, pointer(packed), len(parts), pointer(reports), cancel
    )
    result = owned(own.engine, handle)
    diagnostics = tuple(
        diagnostic(part.id, side, row)
        for part, config, row in zip(parts, values, reports, strict=True)
        if all(config)
    )
    return result, diagnostics


REPORT_FLOATS = (
    "total_ms",
    "solve_ms",
    "violation",
    "stationarity",
    "complementarity",
    "max_displacement",
    "complementarity_relative",
    "objective",
)
REPORT_INTS = ("iterations", "samples", "pinned", "skipped_triangles")


def diagnostic(part: str, side: str, row: Any) -> TissueDiagnostic:
    counts = dict(zip(REPORT_INTS, map(int, row[:4]), strict=True))
    values: dict[str, Any] = dict(zip(REPORT_FLOATS, map(float, row[4:12]), strict=True))
    status = "ITERATION_LIMIT" if row[12] else "CONVERGED"
    return TissueDiagnostic(stage="rest", status=status, part=part, side=side, **counts, **values)
