"""Owned preview/exterior query copies; the native mesh retains material provenance."""

from dataclasses import dataclass
from enum import IntEnum

from .mesh import GeometryEngine, Mesh, U


class Mode(IntEnum):
    PREVIEW = 0
    CONFIRMED = 1


@dataclass(frozen=True, eq=False)
class Query:
    mesh: Mesh
    resources: tuple[Mesh, ...]
    bytes: int


def configure(engine: GeometryEngine) -> None:
    import ctypes as c

    engine.bind("af_surface_query", [U, U, c.c_int, U], U)
    engine.bind("af_mesh_retained_bytes", [c.POINTER(U), c.c_int], U)


def retained_bytes(engine: GeometryEngine, resources: tuple[Mesh, ...]) -> int:
    handles = (U * len(resources))(*(mesh.handle for mesh in resources))
    size = int(engine.library.af_mesh_retained_bytes(handles, len(resources)))
    engine.check(size == 0)
    return size


def prepare(source: Mesh, base: Mesh | None, mode: Mode, cancel: int = 0) -> Query:
    engine = source.engine
    key = (source.handle, base.handle if base else 0, int(mode))
    cached = engine.surface_queries.get(key)
    if cached is not None:
        return cached
    handle = engine.library.af_surface_query(*key, cancel)
    engine.check(not handle)
    mesh = Mesh(engine, handle)
    resources = (mesh, source, base) if base else (mesh, source)
    size = retained_bytes(engine, resources)
    result = Query(mesh, resources, size)
    return engine.surface_queries.store(key, result, size)
