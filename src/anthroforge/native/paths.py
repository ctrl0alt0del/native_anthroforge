"""Owned native paths; array leases keep the underlying allocation alive."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve

from .construction import curve_records
from .mesh import INT64, D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_path_evaluate", [D, c.c_int, c.c_int, c.c_int, c.c_int, U], U)
    engine.bind("af_path_restore", [D, D, c.c_int, c.c_int], U)
    engine.bind("af_path_info", [U, INT64, D])
    engine.bind("af_path_buffer", [U, c.c_int], c.c_void_p)
    engine.bind("af_path_release", [U], None)
    engine.bind("af_path_sample", [U, c.c_int, c.c_double, c.c_double, D, c.c_int, D, U])
    engine.bind("af_path_body", [U, c.c_int, c.c_int, D, U])


class Path:
    def __init__(self, engine: GeometryEngine, handle: int) -> None:
        engine.check(not handle)
        self.engine, self.handle = engine, handle
        counts, bounds = (c.c_int64 * 3)(), (c.c_double * 6)()
        engine.check(engine.library.af_path_info(handle, counts, bounds))
        self.count, self.closed, self.bytes = counts[0], bool(counts[1]), counts[2]
        self.bounds = tuple(bounds)

    def array(self, kind: int = 0) -> Any:
        if kind not in (0, 1):
            raise ValueError("Unknown path buffer.")
        address = self.engine.library.af_path_buffer(self.handle, kind)
        self.engine.check(not address)
        count = self.count * (11 if kind == 0 else 1)
        buffer = c.cast(address, c.POINTER(c.c_double * count)).contents
        buffer._path_owner = self  # type: ignore[attr-defined]  # ctypes lease retained by NumPy.
        array = np.frombuffer(buffer, dtype=np.float64)
        array = array.reshape((self.count, 11)) if kind == 0 else array
        array.flags.writeable = False
        return array

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_path_release(self.handle)


def evaluate(engine: GeometryEngine, curve: Curve, cancel: int = 0, records: Any = None) -> Path:
    if curve.engine not in ("BEZIER", "POLYLINE"):
        raise ValueError("The routed path engine is not available in this development increment.")
    records = curve_records(curve) if records is None else doubles(records)
    handle = engine.library.af_path_evaluate(
        pointer(records),
        len(curve.points),
        int(curve.engine == "POLYLINE"),
        curve.closed,
        curve.resolution,
        cancel,
    )
    return Path(engine, handle)


def restore(engine: GeometryEngine, samples: Any, parameters: Any, closed: bool) -> Path:
    samples, parameters = doubles(samples), doubles(parameters)
    if samples.ndim != 2 or samples.shape[1] != 11 or parameters.shape != (len(samples),):
        raise ValueError("Invalid stored path buffer shapes.")
    if not np.isfinite(samples).all() or not np.isfinite(parameters).all():
        raise ValueError("Path buffers must be finite.")
    handle = engine.library.af_path_restore(
        pointer(samples), pointer(parameters), len(samples), closed
    )
    return Path(engine, handle)


def sample(
    path: Path,
    count: int,
    start: float,
    span: float,
    matrix: Any,
    reverse: bool = False,
    cancel: int = 0,
) -> Any:
    output, frame = np.empty((count, 11)), doubles(matrix)
    operation = path.engine.library.af_path_sample
    args = (path.handle, count, start, span, pointer(frame), reverse, pointer(output), cancel)
    path.engine.check(operation(*args))
    return output


def body(path: Path, closed_start: int = 0, reverse: bool = False, cancel: int = 0) -> Any:
    output = np.empty((path.count, 11))
    path.engine.check(
        path.engine.library.af_path_body(
            path.handle, reverse, closed_start, pointer(output), cancel
        )
    )
    return output
