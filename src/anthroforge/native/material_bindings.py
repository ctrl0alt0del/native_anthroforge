"""Owned bind-topology geometry resolves retained material coordinates on current output."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, Mesh, U, doubles, pointer
from .tissue_shapes import owned


def configure(engine: Any) -> None:
    engine.bind("af_material_binding_validate", [U, U, D, c.c_int, D, c.POINTER(c.c_int), U])


def validate(reference: Mesh, current: Mesh, world: Any, records: Any, cancel: int = 0) -> Any:
    rows, transform = doubles(records), doubles(world)
    if rows.ndim != 2 or rows.shape[1] != 28 or transform.size != 16:
        raise ValueError("Material validation requires records and one world frame.")
    output = np.empty(len(rows), dtype=np.int32)
    args = reference.handle, current.handle, pointer(transform), len(rows), pointer(rows)
    reference.engine.check(
        reference.engine.library.af_material_binding_validate(
            *args,
            output.ctypes.data_as(c.POINTER(c.c_int)),
            cancel,
        )
    )
    return output


def resolve(reference: Mesh, current: Mesh, records: Any, cancel: int = 0) -> Mesh:
    rows = doubles(records)
    if rows.ndim != 2 or rows.shape[1] != 28:
        raise ValueError("Retained material resolution requires captured attachment records.")
    handle = current.engine.library.af_material_binding_surface(
        reference.handle, current.handle, len(rows), pointer(rows), cancel
    )
    return owned(current.engine, handle)


def frames(reference: Mesh, current: Mesh, world: Any, records: Any, cancel: int = 0) -> Any:
    rows, transform = doubles(records), doubles(world)
    if rows.ndim != 2 or rows.shape[1] != 28 or transform.size != 16:
        raise ValueError("Material frames require captured records and one world transform.")
    output = np.empty((len(rows), 16))
    if len(rows):
        evaluate_frames(reference, current, transform, rows, output, cancel)
    return output


def evaluate_frames(
    reference: Mesh, current: Mesh, transform: Any, rows: Any, output: Any, cancel: int
) -> None:
    args = (
        reference.handle,
        current.handle,
        pointer(transform),
        len(rows),
        pointer(rows),
        pointer(output),
        cancel,
    )
    current.engine.check(current.engine.library.af_material_binding_frames(*args))
