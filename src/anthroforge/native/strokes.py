"""Mutable provisional native strokes; only frozen samples become authored inputs."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_stroke_create", [c.c_int, c.POINTER(U), D, D, D], U)
    engine.bind("af_stroke_release", [U], None)
    engine.bind("af_stroke_append", [U, D, c.c_int])
    engine.bind("af_stroke_probe", [U, D, D])
    engine.bind("af_stroke_read", [U, c.c_int, c.c_int, D])
    engine.bind("af_stroke_pop", [U])
    engine.bind("af_drawing_plane", [D, D])
    engine.bind("af_stroke_view", [U, D])
    engine.bind("af_stroke_batch", [U, c.c_int, D, c.c_int, U])
    engine.bind("af_stroke_bytes", [U], U)


def plane(engine: GeometryEngine, frame: Any) -> list[float]:
    data, output = doubles(frame), np.empty(6)
    if data.size != 16:
        raise ValueError("Plane frame must have sixteen values.")
    engine.check(engine.library.af_drawing_plane(pointer(data), pointer(output)))
    return list(output.tolist())


class Stroke:
    def __init__(self, engine: GeometryEngine, meshes: Any, frames: Any, plane: Any, options: Any):
        handles = np.ascontiguousarray(meshes, dtype=np.uint64)
        frames, plane, options = doubles(frames), doubles(plane), doubles(options)
        if frames.size != len(handles) * 16 or plane.size != 6 or options.size != 4:
            raise ValueError("Stroke needs mesh frames, a depth plane and projection settings.")
        self.engine, self.count = engine, 0
        self.handle = engine.library.af_stroke_create(
            len(handles),
            handles.ctypes.data_as(c.POINTER(U)),
            pointer(frames),
            pointer(plane),
            pointer(options),
        )
        engine.check(not self.handle)

    @property
    def bytes(self) -> int:
        return int(self.engine.library.af_stroke_bytes(self.handle))

    def batch(self, rays: Any, interpolate: bool = True, cancel: int = 0) -> int:
        data = doubles(rays)
        if data.ndim != 2 or data.shape[1] != 9 or len(data) > 100000:
            raise ValueError("Pointer batch requires at most 100000 ray/screen/radius rows.")
        count = self.engine.library.af_stroke_batch(
            self.handle, len(data), pointer(data), interpolate, cancel
        )
        self.engine.check(count < 0)
        self.count = count
        return self.count

    def append(self, ray: Any, interpolate: bool = True) -> int:
        data = pointer_input(ray)
        count = self.engine.library.af_stroke_append(self.handle, pointer(data), interpolate)
        self.engine.check(count < 0)
        self.count = count
        return self.count

    def probe(self, ray: Any) -> list[float]:
        data, output = pointer_input(ray), np.empty(4)
        self.engine.check(
            self.engine.library.af_stroke_probe(self.handle, pointer(data), pointer(output))
        )
        return list(output.tolist())

    def read(self, start: int = 0) -> Any:
        output = np.empty((max(0, self.count - start), 4))
        written = self.engine.library.af_stroke_read(
            self.handle, start, len(output), pointer(output)
        )
        self.engine.check(written < 0)
        return output[:written]

    def pop(self) -> None:
        self.count = self.engine.library.af_stroke_pop(self.handle)
        self.engine.check(self.count < 0)

    def view(self, normal: Any) -> None:
        data = doubles(normal)
        if data.shape != (3,):
            raise ValueError("View normal requires three values.")
        self.engine.check(self.engine.library.af_stroke_view(self.handle, pointer(data)))

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_stroke_release(self.handle)


def pointer_input(value: Any) -> Any:
    data = doubles(value)
    if data.shape != (9,):
        raise ValueError("Stroke pointer requires a ray, screen XY and radius.")
    return data
