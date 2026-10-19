"""Owned bind-topology geometry resolves retained material coordinates on current output."""

from typing import Any

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
