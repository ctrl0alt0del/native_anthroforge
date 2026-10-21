"""Bounded diagnostic output using the production stacking material masks."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, U, pointer


def footprint(session: Any, receiver: int, provider: int, cancel: int = 0) -> dict[str, Any]:
    engine = session.engine
    engine.bind("af_stack_footprint", [U, U, U, D, c.c_int, INT64, U])
    lines, summary = np.empty((8192, 3)), np.zeros(3, dtype=np.int64)
    args = session.handle, receiver, provider, pointer(lines), len(lines)
    engine.check(engine.library.af_stack_footprint(*args, summary.ctypes.data_as(INT64), cancel))
    return report(lines, summary)


def report(lines: Any, summary: Any) -> dict[str, Any]:
    return dict(
        lines=lines[: summary[0]].tolist(),
        polygons=int(summary[1]),
        truncated=bool(summary[2]),
        space="world",
        surface="intrinsic receiver",
    )
