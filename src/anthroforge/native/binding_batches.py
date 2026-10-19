"""Owned immutable batches of shared anatomical point bindings."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer


@dataclass(frozen=True, eq=False)
class BindingBatch:
    records: Any

    def __post_init__(self) -> None:
        data = self.records
        if data.dtype != np.float64 or not data.flags.c_contiguous or not np.isfinite(data).all():
            raise ValueError("Binding batches require finite contiguous double records.")
        if data.ndim != 2 or data.shape[1] != 28 or not 0 < len(data) <= 262144:
            raise ValueError("Binding batches require between one and 262144 point records.")
        data.flags.writeable = False

    @property
    def bytes(self) -> int:
        return int(self.records.nbytes)


def positions(engine: Any, frames: Any, local_frame: Any, offset: float, cancel: int) -> Any:
    data, frame = doubles(frames), doubles(local_frame)
    if data.ndim != 2 or data.shape[1] != 16 or frame.size != 16:
        raise ValueError("Goal positions require resolved attachment frames and a local frame.")
    engine.bind("af_attachment_goal_points", [D, c.c_int, D, c.c_double, D, U])
    output = np.empty((len(data), 3))
    engine.check(
        engine.library.af_attachment_goal_points(
            pointer(data), len(data), pointer(frame), offset, pointer(output), cancel
        )
    )
    return output
