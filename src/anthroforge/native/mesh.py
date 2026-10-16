"""Owned native mesh handles; all geometric evaluation is native."""

import ctypes as c
from pathlib import Path
from threading import Event
from typing import Any

import numpy as np

from .bridge import NativeEngine

D = c.POINTER(c.c_double)
INT64 = c.POINTER(c.c_int64)
U = c.c_uint64


def doubles(values: Any) -> Any:
    return np.ascontiguousarray(values, dtype=np.float64)


def pointer(array: Any) -> Any:
    return array.ctypes.data_as(D)


class GeometryEngine(NativeEngine):
    def __init__(self, path: Path | None = None) -> None:
        super().__init__(path)
        self._mesh_signatures()
        self._query_signatures()

    def bind(self, name: str, args: list[Any], result: Any = c.c_int) -> None:
        function = getattr(self.library, name)
        function.argtypes, function.restype = args, result

    def _mesh_signatures(self) -> None:
        self.bind("af_last_error", [], c.c_char_p)
        self.bind("af_mesh_import", [c.c_char_p, c.c_double, c.c_int, U], U)
        self.bind("af_mesh_create", [D, c.c_int64, INT64, INT64, c.c_int64], U)
        self.bind("af_mesh_release", [U], None)
        self.bind("af_mesh_sizes", [U, INT64])
        self.bind("af_mesh_buffer", [U, c.c_int], c.c_void_p)
        self.bind("af_mesh_bounds", [U, D])
        self.bind("af_cancel_create", [], U)
        self.bind("af_cancel_request", [U], None)
        self.bind("af_cancel_release", [U], None)

    def _query_signatures(self) -> None:
        self.bind("af_transform", [D, D])
        self.bind("af_decompose", [D, D])
        self.bind("af_point", [D, D, D])
        self.bind("af_pick", [U, D, D, D, D])
        self.bind("af_capture", [U, U, D, D, D, D, c.c_int, c.c_int, c.c_int, c.c_int, D])
        self.bind("af_move_origin", [D, D, D, D, D])
        self.bind("af_anchor_points", [U, D, D, D, D, D])
        ints = c.POINTER(c.c_int)
        self.bind(
            "af_propagate", [c.c_int, c.POINTER(U), ints, D, D, D, ints, ints, ints, ints, ints, U]
        )

    def check(self, status: int) -> None:
        if status:
            raise ValueError(self.library.af_last_error().decode("utf-8", errors="replace"))

    def transform(self, values: Any) -> tuple[float, ...]:
        source, output = doubles(values), np.empty(16)
        if source.size != 9:
            raise ValueError("Transform requires position, Euler degrees, and scale: nine values.")
        self.check(self.library.af_transform(pointer(source), pointer(output)))
        return tuple(output.tolist())

    def decompose(self, matrix: Any) -> list[float]:
        source, output = doubles(matrix), np.empty(9)
        self.check(self.library.af_decompose(pointer(source), pointer(output)))
        return list(output.tolist())

    def world_point(self, matrix: Any, point: Any) -> list[float]:
        source, local, output = doubles(matrix), doubles(point), np.empty(3)
        self.check(self.library.af_point(pointer(source), pointer(local), pointer(output)))
        return list(output.tolist())

    def import_mesh(self, path: Path, units: float, y_up: bool, cancel: int = 0) -> "Mesh":
        handle = self.library.af_mesh_import(str(path).encode("utf-8"), units, int(y_up), cancel)
        self.check(not handle)
        return Mesh(self, handle)

    def create_mesh(self, vertices: Any, corners: Any, offsets: Any) -> "Mesh":
        vertices, corners = doubles(vertices), np.ascontiguousarray(corners, dtype=np.int64)
        offsets = np.ascontiguousarray(offsets, dtype=np.int64)
        validate_arrays(vertices, corners, offsets)
        handle = self.library.af_mesh_create(
            pointer(vertices),
            len(vertices),
            corners.ctypes.data_as(INT64),
            offsets.ctypes.data_as(INT64),
            len(offsets) - 1,
        )
        self.check(not handle)
        return Mesh(self, handle)

    def pick(self, mesh: "Mesh", matrix: Any, origin: Any, direction: Any) -> list[float] | None:
        arrays = [doubles(value) for value in (matrix, origin, direction)]
        output = np.empty(10)
        status = self.library.af_pick(mesh.handle, *(pointer(a) for a in arrays), pointer(output))
        if status < 0:
            self.check(status)
        return list(output.tolist()) if status else None


def validate_arrays(vertices: Any, corners: Any, offsets: Any) -> None:
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.isfinite(vertices).all():
        raise ValueError("Invalid vertex array.")
    if offsets.ndim != 1 or len(offsets) < 2 or offsets[0] != 0:
        raise ValueError("Invalid polygon offsets.")
    if offsets[-1] != len(corners) or (np.diff(offsets) < 3).any():
        raise ValueError("Polygon offsets do not match corner data.")
    if corners.ndim != 1 or (corners < 0).any() or (corners >= len(vertices)).any():
        raise ValueError("Invalid vertex references.")


class Mesh:
    def __init__(self, engine: GeometryEngine, handle: int) -> None:
        self.engine, self.handle = engine, handle
        sizes = (c.c_int64 * 5)()
        engine.check(engine.library.af_mesh_sizes(handle, sizes))
        self.counts = tuple(sizes)
        bounds = (c.c_double * 6)()
        engine.check(engine.library.af_mesh_bounds(handle, bounds))
        self.bounds = tuple(bounds)

    def array(self, kind: int) -> Any:
        vertices, faces, corners, triangles, _ = self.counts
        shapes = ((vertices, 3), (corners,), (faces + 1,), (triangles, 3), (triangles,))
        types = (c.c_double, c.c_int64, c.c_int64, c.c_int32, c.c_int64)
        address = self.engine.library.af_mesh_buffer(self.handle, kind)
        value = np.ctypeslib.as_array(c.cast(address, c.POINTER(types[kind])), shapes[kind])
        value.flags.writeable = False
        return value

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_mesh_release(self.handle)


class NativeCancellation(Event):
    def __init__(self, engine: GeometryEngine) -> None:
        super().__init__()
        self.engine = engine
        self.handle = int(engine.library.af_cancel_create())

    def set(self) -> None:
        super().set()
        self.engine.library.af_cancel_request(self.handle)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_cancel_release(self.handle)
