"""Owned native mesh handles; all geometric evaluation is native."""

import ctypes as c
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING, Any

import numpy as np

from .base_cache import BaseCache
from .bridge import NativeEngine
from .resource_cache import ResourceCache

if TYPE_CHECKING:
    from .routing_scene import RoutingScene
    from .surface_queries import Query
    from .tissue_stacking import MaterialLease

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
        self._construction_signatures()
        self._resource_caches()
        self.resource_observer: Any = None

    def _resource_caches(self) -> None:
        self.bases = BaseCache()
        self.routing_scenes: ResourceCache[RoutingScene] = ResourceCache(
            64 * 1024 * 1024, 8, "routing_scene"
        )
        self.tissue_materials: ResourceCache[MaterialLease] = ResourceCache(
            64 * 1024 * 1024, 64, "tissue_material"
        )
        self._query_caches()

    def _query_caches(self) -> None:
        self.collision_checks: ResourceCache[Any] = ResourceCache(
            128 * 1024 * 1024, 1, "collision_pairs"
        )
        self.surface_queries: ResourceCache[Query] = ResourceCache(
            64 * 1024 * 1024, 64, "surface_query"
        )
        self.paint_surfaces: ResourceCache[Any] = ResourceCache(
            64 * 1024 * 1024, 4, "paint_surface"
        )

    def caches(self) -> tuple[Any, ...]:
        return (
            self.bases,
            self.routing_scenes,
            self.tissue_materials,
            self.surface_queries,
            self.paint_surfaces,
            self.collision_checks,
        )

    def clear_caches(self) -> None:
        for cache in self.caches():
            cache.clear()

    def _construction_signatures(self) -> None:
        from . import bodies, components, construction, curve_surfaces, falloff, scene, topology
        from .control_geometry import configure as configure_control_geometry

        for module in (bodies, components, construction, curve_surfaces, falloff, scene, topology):
            module.configure(self)
        configure_control_geometry(self)
        self._curve_signatures()
        self._inspection_signatures()

    def _inspection_signatures(self) -> None:
        from . import inspection, inspection_goals, painting, routing_trace, sections

        inspection.configure(self)
        inspection_goals.configure(self)
        painting.configure(self)
        sections.configure(self)
        routing_trace.configure(self)

    def _curve_signatures(self) -> None:
        from . import curve_editing, curve_queries, drawing, path_editing, paths, routing, strokes

        for module in (
            curve_editing,
            curve_queries,
            drawing,
            path_editing,
            paths,
            routing,
            strokes,
        ):
            module.configure(self)
        self._binding_signatures()

    def _binding_signatures(self) -> None:
        from . import attachment_fields, attachment_weights, path_collisions, point_attachments
        from .mesh_quality import configure as configure_quality
        from .routing_scene import configure
        from .surface_queries import configure as configure_queries

        for module in (attachment_fields, attachment_weights, path_collisions, point_attachments):
            module.configure(self)
        configure(self)
        configure_quality(self)
        configure_queries(self)

    def bind(self, name: str, args: list[Any], result: Any = c.c_int) -> None:
        function = getattr(self.library, name)
        function = getattr(function, "_profile_original", function)
        function.argtypes, function.restype = args, result
        if self.profile_bind is not None:
            self.profile_bind(name, function)

    def _mesh_signatures(self) -> None:
        self.bind("af_last_error", [], c.c_char_p)
        self.bind("af_mesh_import", [c.c_char_p, c.c_double, c.c_int, U], U)
        self.bind("af_mesh_create", [D, c.c_int64, INT64, INT64, c.c_int64], U)
        self.bind("af_mesh_release", [U], None)
        self.bind("af_mesh_sizes", [U, INT64])
        self.bind("af_mesh_prepared", [U])
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
        self.bind("af_anchor_points", [U, D, D, D, D, D, U])
        ints = c.POINTER(c.c_int)
        self.bind(
            "af_propagate",
            [c.c_int, c.POINTER(U), ints, D, D, D, ints, ints, ints, ints, ints, U, c.POINTER(U)],
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


def validate_arrays(vertices: Any, corners: Any, offsets: Any, allow_empty: bool = False) -> None:
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.isfinite(vertices).all():
        raise ValueError("Invalid vertex array.")
    minimum = 1 if allow_empty and len(vertices) == 0 else 2
    if offsets.ndim != 1 or len(offsets) < minimum or offsets[0] != 0:
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
        state = engine.library.af_mesh_prepared(handle)
        engine.check(state < 0)
        self.prepared = bool(state)
        if engine.resource_observer is not None:
            engine.resource_observer(self)

    def array(self, kind: int) -> Any:
        vertices, faces, corners, triangles, _ = self.counts
        shapes = ((vertices, 3), (corners,), (faces + 1,), (triangles, 3), (triangles,))
        types = (c.c_double, c.c_int64, c.c_int64, c.c_int32, c.c_int64)
        address = self.engine.library.af_mesh_buffer(self.handle, kind)
        value = (
            np.empty(shapes[kind], dtype=types[kind])
            if shapes[kind][0] == 0
            else np.ctypeslib.as_array(c.cast(address, c.POINTER(types[kind])), shapes[kind])
        )
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
