"""Owned bind-topology geometry resolves retained material coordinates on current output."""

from typing import Any

import numpy as np

from .mesh import Mesh, doubles, pointer
from .tissue_shapes import owned


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
