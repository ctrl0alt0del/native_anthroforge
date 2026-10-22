"""Immutable native material frames/operators qualified by accepted base and mode."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, Mesh, U
from .tissue_inflation import Inflation


def configure(engine: GeometryEngine) -> None:
    pointer = c.POINTER(Inflation)
    engine.bind("af_tissue_preparation_create", [U, pointer, c.c_int, U], U)
    engine.bind("af_tissue_preparation_release", [U], None)
    engine.bind("af_tissue_preparation_bytes", [U, c.c_int], U)
    engine.bind("af_tissue_inflate_prepared", [U, pointer, c.c_int, D, c.c_int, U, c.c_int], U)


class Preparation:
    def __init__(self, base: Mesh, settings: Any, cancel: int) -> None:
        self.engine, self.resources = base.engine, (base,)
        self.handle = self.engine.library.af_tissue_preparation_create(
            base.handle, settings, len(settings), cancel
        )
        self.engine.check(not self.handle)
        self.bytes = int(self.engine.library.af_tissue_preparation_bytes(self.handle, False))
        self.retained_bytes = int(
            self.engine.library.af_tissue_preparation_bytes(self.handle, True)
        )
        if self.engine.resource_observer is not None:
            self.engine.resource_observer(self)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_tissue_preparation_release(self.handle)


def mode(settings: Any) -> tuple[int, int]:
    value = settings.mode if settings.enabled else 0
    if value == 1 and settings.amount <= 0:
        value = 0
    return value, settings.direction if value == 2 else 0


def acquire(base: Mesh, settings: Any, cancel: int) -> Preparation:
    cache = base.engine.tissue_preparations
    key = (base.handle, tuple(mode(value) for value in settings))
    found = cache.get(key)
    if found is not None:
        return found
    value = Preparation(base, settings, cancel)
    return cache.store(key, value, value.retained_bytes)
