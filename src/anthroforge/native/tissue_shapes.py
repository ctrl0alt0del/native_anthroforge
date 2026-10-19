"""Batched native radial, sweep and normal-shell construction adapters."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.tissue_settings import TissueInflation

from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


class Shape(c.Structure):
    _fields_ = [(name, c.c_int) for name in ("enabled", "reverse", "segments")]
    _fields_ += [
        (name, c.c_double) for name in ("amount", "minimum", "power", "width", "endpoint_taper")
    ]
    _fields_ += [("scale", c.c_double * 3)]


def configure(engine: GeometryEngine) -> None:
    from . import tissue_regions

    tissue_regions.configure(engine)
    shape = c.POINTER(Shape)
    engine.bind("af_tissue_normal_shell", [U, shape, D, c.c_int64, U], U)
    engine.bind("af_tissue_profile_sweep", [D, c.c_int, c.c_int, shape, U], U)
    engine.bind("af_tissue_radial", [D, shape, c.c_int, U], U)
    engine.bind("af_tissue_field_edit", [D, c.c_int64, INT64, c.c_int64, c.c_double, D])


def field_edit(engine: GeometryEngine, count: int, values: Any, indices: Any, weight: float) -> Any:
    source, selected = doubles(values), np.ascontiguousarray(indices, dtype=np.int64)
    if source.ndim != 1 or selected.ndim != 1 or len(source) not in (0, count):
        raise ValueError("Field values and selection must match a flat material domain.")
    output = np.empty(count, dtype=np.float64)
    selection = selected.ctypes.data_as(INT64), len(selected), weight, pointer(output)
    engine.check(
        engine.library.af_tissue_field_edit(
            pointer(source) if len(source) else None, count, *selection
        )
    )
    return output


def pack(settings: TissueInflation, reverse: bool) -> Shape:
    result = Shape(settings.enabled, reverse, settings.segments)
    for name in ("amount", "minimum", "power", "width", "endpoint_taper"):
        setattr(result, name, getattr(settings, name))
    result.scale[:] = settings.scale
    return result


def normal(
    mesh: Mesh, settings: TissueInflation, weights: Any = (), reverse: bool = False, cancel: int = 0
) -> Mesh:
    values, shape = doubles(weights), pack(settings, reverse)
    if values.ndim != 1:
        raise ValueError("Thickness field must be flat.")
    handle = mesh.engine.library.af_tissue_normal_shell(
        mesh.handle, c.byref(shape), pointer(values), len(values), cancel
    )
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)


def sweep(
    engine: GeometryEngine,
    samples: Any,
    closed: bool,
    settings: TissueInflation,
    reverse: bool = False,
    cancel: int = 0,
) -> Mesh:
    values, shape = doubles(samples), pack(settings, reverse)
    if values.ndim != 2 or values.shape[1] != 11:
        raise ValueError("Tissue sweep requires accepted curve samples.")
    handle = engine.library.af_tissue_profile_sweep(
        pointer(values), len(values), closed, c.byref(shape), cancel
    )
    return owned(engine, handle)


def radial(
    engine: GeometryEngine, frame: Any, settings: TissueInflation, resolution: int, cancel: int = 0
) -> Mesh:
    values, shape = doubles(frame), pack(settings, False)
    if values.size != 16:
        raise ValueError("Radial tissue requires an accepted Anchor frame.")
    handle = engine.library.af_tissue_radial(pointer(values), c.byref(shape), resolution, cancel)
    return owned(engine, handle)


def owned(engine: GeometryEngine, handle: int) -> Mesh:
    engine.check(not handle)
    return Mesh(engine, handle)
