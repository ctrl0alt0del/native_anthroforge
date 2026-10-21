"""Owned projection/visibility cache and batched native weight strokes."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .inspection import Comparison
from .mesh import D, Mesh, U, doubles, pointer
from .resource_cache import ResourceCache
from .surface_queries import retained_bytes


def configure(engine: Any) -> None:
    engine.bind("af_paint_prepare", [U, U, c.c_int, c.c_int, D, D, c.POINTER(U), D, c.c_int, U], U)
    engine.bind("af_paint_release", [U], None)
    engine.bind("af_paint_bytes", [U], U)
    engine.bind("af_paint_stroke", [U, D, D, c.c_int, D, D, U], U)


@dataclass(frozen=True)
class Inputs:
    target: Mesh
    reference: Mesh | None
    source: bool
    count: int
    frame: tuple[float, ...]
    view: tuple[float, ...]
    others: tuple[Mesh, ...] = ()
    frames: tuple[tuple[float, ...], ...] = ()


class Prepared:
    def __init__(self, inputs: Inputs, cancel: int) -> None:
        self.engine, self.target = inputs.target.engine, inputs.target
        self.reference, self.count = inputs.reference, inputs.count
        self.resources = (self.target, self.reference or self.target, *inputs.others)
        self.handle = create(inputs, cancel)
        self.engine.check(not self.handle)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_paint_release(self.handle)

    @property
    def bytes(self) -> int:
        return int(self.engine.library.af_paint_bytes(self.handle))


class PaintColors(Comparison):
    def __init__(self, prepared: Prepared, baseline: Any, samples: Any, settings: Any, cancel: int):
        self.engine, self.target, self.reference = prepared.engine, prepared.target, prepared.target
        weights, points, config = doubles(baseline), doubles(samples), doubles(settings)
        validate_arrays(prepared, weights, points, config)
        self.values = np.empty(prepared.count)
        args = prepared.handle, pointer(weights), pointer(points), len(points), pointer(config)
        self.handle = self.engine.library.af_paint_stroke(*args, pointer(self.values), cancel)
        self.engine.check(not self.handle)
        self.read_summary()

    @property
    def bytes(self) -> int:
        return super().bytes + int(self.values.nbytes)


def validate_arrays(prepared: Prepared, weights: Any, points: Any, config: Any) -> None:
    if (
        weights.shape != (prepared.count,)
        or points.ndim != 2
        or points.shape[1] != 2
        or config.shape != (5,)
    ):
        raise ValueError("Invalid brush input dimensions.")


def create(value: Inputs, cancel: int) -> int:
    handles = (U * len(value.others))(*(m.handle for m in value.others))
    matrices, camera, world = doubles(value.frames), doubles(value.view), doubles(value.frame)
    args: tuple[Any, ...] = (
        value.target.handle,
        value.reference.handle if value.reference else 0,
        value.source,
        value.count,
    )
    args += pointer(world), pointer(camera), handles, pointer(matrices), len(value.others), cancel
    return int(value.target.engine.library.af_paint_prepare(*args))


def prepare(inputs: Inputs, cancel: int = 0) -> Prepared:
    if (
        len(inputs.frame) != 16
        or len(inputs.frames) != len(inputs.others)
        or len(inputs.view) != 14
        or any(len(f) != 16 for f in inputs.frames)
    ):
        raise ValueError("Invalid paint camera or scene transforms.")
    key = (inputs,)
    cache: ResourceCache[Prepared] = inputs.target.engine.paint_surfaces
    existing = cache.get(key)
    if existing is not None:
        return existing
    value = Prepared(inputs, cancel)
    return cache.store(key, value, value.bytes + retained_bytes(value.engine, value.resources))
