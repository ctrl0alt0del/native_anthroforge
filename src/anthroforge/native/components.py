"""Batched transforms and picking for cached construction-control coordinates."""

import ctypes as c
import weakref
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_points_transform", [D, c.c_int, D, D])
    engine.bind("af_component_pick", [D, c.c_int, D, D, c.c_double, c.c_int])
    engine.bind("af_component_hits", [D, c.c_int, D, D, c.c_double, D])
    engine.bind("af_component_index_create", [D, c.c_int, c.c_int, c.POINTER(c.c_int)], U)
    engine.bind("af_component_index_release", [U], None)
    engine.bind("af_component_index_pick", [U, D, D, c.c_double, c.c_int])
    engine.bind("af_component_index_closest", [U, D, D, D, c.c_int])


class PickIndex:
    def closest(self, origin: Any, direction: Any, normal: Any, perspective: bool) -> int:
        values = [doubles(value) for value in (origin, direction, normal)]
        if any(value.shape != (3,) for value in values):
            raise ValueError("Point projection requires three-dimensional rays and a view normal.")
        return int(
            self.engine.library.af_component_index_closest(
                self.handle, *(pointer(value) for value in values), perspective
            )
        )

    def __init__(
        self, engine: GeometryEngine, points: Any, segments: bool = False, labels: Any = None
    ) -> None:
        self.engine = engine
        self.handle = create_index(engine, points, segments, labels)
        self._release = weakref.finalize(
            self, engine.library.af_component_index_release, self.handle
        )

    def pick(self, origin: Any, direction: Any, radius: float, depth: int = 0) -> int:
        start, ray = doubles(origin), doubles(direction)
        return int(
            self.engine.library.af_component_index_pick(
                self.handle, pointer(start), pointer(ray), radius, depth
            )
        )


def create_index(engine: GeometryEngine, points: Any, segments: bool, labels: Any) -> int:
    data = doubles(points).reshape((-1, 3))
    count = len(data) // (2 if segments else 1)
    identifiers = (
        np.arange(count, dtype=np.int32) if labels is None else np.asarray(labels, dtype=np.int32)
    )
    if len(identifiers) != count or (segments and len(data) % 2):
        raise ValueError("Picking labels and coordinates must match.")
    handle = engine.library.af_component_index_create(
        pointer(data), count, segments, identifiers.ctypes.data_as(c.POINTER(c.c_int))
    )
    engine.check(not handle)
    return int(handle)


def transformed(engine: GeometryEngine, points: Any, matrix: Any) -> Any:
    data, frame = doubles(points).reshape((-1, 3)), doubles(matrix)
    output = np.empty_like(data)
    engine.check(
        engine.library.af_points_transform(
            pointer(data), len(data), pointer(frame), pointer(output)
        )
    )
    return output


def pick(
    engine: GeometryEngine, points: Any, origin: Any, direction: Any, radius: float, depth: int = 0
) -> int:
    data, start, ray = doubles(points), doubles(origin), doubles(direction)
    return int(
        engine.library.af_component_pick(
            pointer(data), len(data), pointer(start), pointer(ray), radius, depth
        )
    )


def hits(engine: GeometryEngine, points: Any, origin: Any, direction: Any, radius: float) -> Any:
    data, start, ray = doubles(points), doubles(origin), doubles(direction)
    output = np.empty((len(data), 2))
    count = engine.library.af_component_hits(
        pointer(data), len(data), pointer(start), pointer(ray), radius, pointer(output)
    )
    return output[:count]
