"""Allocation receipts for cache retention; shared resources are charged once."""

import ctypes as c
from typing import Any


def mesh_receipt(mesh: Any) -> dict[Any, int]:
    row = (c.c_uint64 * 7)()
    engine = mesh.engine
    engine.bind("af_mesh_memory_receipt", [c.c_uint64, c.POINTER(c.c_uint64)])
    engine.check(engine.library.af_mesh_memory_receipt(mesh.handle, row))
    return {("mesh", engine.library._handle, row[1]): sum(row[2:5])}


def own_receipt(value: Any, fallback: int) -> dict[Any, int]:
    from .mesh import Mesh
    from .surface_queries import Query

    if isinstance(value, Mesh):
        return mesh_receipt(value)
    size = 0 if isinstance(value, Query) else int(getattr(value, "bytes", fallback))
    if not isinstance(value, Query) and not getattr(value, "resources", ()):
        size = max(size, fallback)
    return {(type(value).__name__, id(value)): size}


def footprint(value: Any, fallback: int) -> dict[Any, int]:
    result = own_receipt(value, fallback)
    for resource in getattr(value, "resources", ()):
        result.update(own_receipt(resource, 0))
    return result


class Allocations:
    def __init__(self) -> None:
        self.entries: dict[Any, tuple[int, int]] = {}
        self.bytes = 0

    def add(self, receipt: dict[Any, int]) -> None:
        for key, size in receipt.items():
            previous, count = self.entries.get(key, (0, 0))
            self.entries[key] = (max(previous, size), count + 1)
            self.bytes += max(previous, size) - previous

    def remove(self, receipt: dict[Any, int]) -> None:
        for key in receipt:
            size, count = self.entries[key]
            if count == 1:
                self.entries.pop(key)
                self.bytes -= size
            else:
                self.entries[key] = (size, count - 1)
