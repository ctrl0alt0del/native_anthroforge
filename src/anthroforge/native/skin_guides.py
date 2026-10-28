"""Native topology samples are copied once into owned worker inputs."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import INT64, D, Mesh, U, doubles, pointer
from .paths import Path


@dataclass(frozen=True)
class Guides:
    samples: Any
    points: Any
    offsets: Any
    regions: Any = None


def configure(engine: Any) -> None:
    from .skin_guide_batch import Input

    engine.bind("af_skin_guides_merge", [c.POINTER(Input), c.c_int, U], U)
    engine.bind("af_skin_guides_regions", [U, INT64, c.c_int64], c.c_int64)
    engine.bind("af_skin_guides_charts", [U, U, D, c.c_int, U], U)
    engine.bind("af_skin_guides_path", [U, D, U], U)
    engine.bind("af_skin_guides_sizes", [U, INT64])
    engine.bind("af_skin_guides_copy", [U, D, D, INT64, INT64])
    engine.bind("af_skin_guides_release", [U], None)


def frame_buffer(frame: Any) -> Any:
    values = doubles(frame)
    if values.size != 16:
        raise ValueError("FLOW frame requires sixteen matrix entries.")
    return values


def charts(base: Mesh, current: Mesh, frame: Any, reverse: bool, cancel: int = 0) -> Guides:
    if base.engine is not current.engine:
        raise ValueError("FLOW meshes must belong to the same native engine.")
    matrix = frame_buffer(frame)
    handle = base.engine.library.af_skin_guides_charts(
        base.handle, current.handle, pointer(matrix), reverse, cancel
    )
    return consume(base.engine, handle)


def path(source: Path, frame: Any, cancel: int = 0) -> Guides:
    matrix = frame_buffer(frame)
    handle = source.engine.library.af_skin_guides_path(source.handle, pointer(matrix), cancel)
    return consume(source.engine, handle)


def consume(engine: Any, handle: int) -> Guides:
    engine.check(not handle)
    try:
        return copy(engine, handle)
    finally:
        engine.library.af_skin_guides_release(handle)


def copy(engine: Any, handle: int) -> Guides:
    sizes = (c.c_int64 * 3)()
    engine.check(engine.library.af_skin_guides_sizes(handle, sizes))
    samples, points = np.empty((sizes[0], 10)), np.empty((sizes[1], 3))
    offsets = np.empty(sizes[2], dtype=np.int64)
    engine.check(
        engine.library.af_skin_guides_copy(
            handle, pointer(samples), pointer(points), offsets.ctypes.data_as(INT64), sizes
        )
    )
    return Guides(samples, points, offsets, regions(engine, handle))


def regions(engine: Any, handle: int) -> Any:
    method = engine.library.af_skin_guides_regions
    count = method(handle, None, 0)
    engine.check(count < 0)
    output = np.empty((count, 2), dtype=np.int64)
    engine.check(method(handle, output.ctypes.data_as(INT64), count) < 0)
    return output
