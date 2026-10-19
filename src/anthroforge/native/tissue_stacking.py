"""Batch authored settings; native leases own material preparation and reassembly."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.entities import IDENTITY
from anthroforge.core.tissue_parts import active

from . import tissue_relaxation
from .mesh import INT64, Mesh, pointer
from .stacking_abi import Domain
from .tissue_inflation import Inflation, pack
from .tissue_shapes import owned
from .tissue_stack_abi import Source, configure


class MaterialLease:
    def __init__(self, base: Mesh, rest: Mesh, own: Mesh, item: Any, **options: Any) -> None:
        configure(base.engine)
        source, _buffers = packed(base, rest, own, item, **options)
        self.engine = base.engine
        self.handle = self.engine.library.af_tissue_stack_prepare(
            c.byref(source), options.get("cancel", 0)
        )
        self.engine.check(not self.handle)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_tissue_stack_release(self.handle)

    def domain(self, identity: int, family: int = 0, root: int = 0, enabled: bool = True) -> Domain:
        result = Domain(id=identity, family=family, root=root, enabled=enabled, allowance=0.5)
        self.engine.check(self.engine.library.af_tissue_stack_domain(self.handle, c.byref(result)))
        return result


def inflations(item: Any, side: str) -> Any:
    parts, reverse = active(item), bool(item.reverse) != (side == "b")
    return (Inflation * len(parts))(
        *(inflation(getattr(p, side).inflation, reverse) for p in parts)
    )


def inflation(value: Any, reverse: bool) -> Inflation:
    if value.mode == "NORMAL":
        return Inflation(enabled=value.enabled, reverse=reverse)
    return pack(value, reverse)


def packed(
    base: Mesh, rest: Mesh, own: Mesh, item: Any, **options: Any
) -> tuple[Source, list[Any]]:
    side = options.get("side", "a")
    values = inflations(item, side)
    regions, buffers = fixed_regions(item)
    result = Source(base=base.handle, rest=rest.handle, own=own.handle, side=1 + (side == "b"))
    result.frame[:] = options.get("frame", IDENTITY)
    result.reverse, result.cropped = item.reverse, item.crop.enabled
    result.crop[:] = (*item.crop.origin, *item.crop.normal, item.crop.positive)
    result.inflation, result.parts = values, len(values)
    result.relaxation = tissue_relaxation.settings(item)
    result.regions, result.region_count = regions, len(regions)
    return result, [values, regions, *buffers, *pins(result, options.get("pins", ((), ())))]


def fixed_regions(item: Any) -> tuple[Any, list[Any]]:
    # Goals are already satisfied by intrinsic output. Stacking constrains displacement to zero.
    rows, buffers = (tissue_relaxation.Region * len(item.constraints))(), []
    fields = {field.name: field for field in item.fields}
    for row, value in zip(rows, item.constraints, strict=True):
        buffers.extend(tissue_relaxation.pack_region(row, value, fields))
    return rows, buffers


def pins(source: Source, values: Any) -> list[Any]:
    indices = np.ascontiguousarray(values[0], dtype=np.int64).reshape((-1, 4))
    weights = np.ascontiguousarray(values[1], dtype=np.float64).reshape((-1, 4))
    if indices.shape != weights.shape:
        raise ValueError("Exact stacking attachment indices and weights must match.")
    source.pins, source.pin_weights = indices.ctypes.data_as(INT64), pointer(weights)
    source.pin_count = len(indices)
    return [indices, weights]


def assemble(
    first: MaterialLease,
    points: Any,
    second: MaterialLease | None = None,
    other: Any = (),
    cancel: int = 0,
) -> Mesh:
    a = np.ascontiguousarray(points, dtype=np.float64).reshape((-1, 3))
    b = np.ascontiguousarray(other, dtype=np.float64).reshape((-1, 3))
    handle = first.engine.library.af_tissue_stack_apply(
        first.handle, second.handle if second else 0, pointer(a), len(a), pointer(b), len(b), cancel
    )
    return owned(first.engine, handle)
