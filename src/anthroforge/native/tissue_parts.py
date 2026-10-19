"""Batch independent per-part inflation settings into the shared native assembly."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer
from .tissue_inflation import Inflation, pack
from .tissue_shapes import owned


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_tissue_inflate_parts", [U, c.POINTER(Inflation), c.c_int, D, U], U)
    engine.bind("af_tissue_envelope", [U, U, c.c_int, U], U)


def evaluate(mesh: Mesh, parts: Any, side: str, reverse: bool, cancel: int = 0) -> Mesh:
    settings = (Inflation * len(parts))(*(pack(getattr(p, side).inflation, reverse) for p in parts))
    connectors = doubles([(p.connector_width, p.connector_fullness) for p in parts])
    handle = mesh.engine.library.af_tissue_inflate_parts(
        mesh.handle, settings, len(parts), pointer(connectors), cancel
    )
    return owned(mesh.engine, handle)


def compose(first: Mesh, second: Mesh, reverse: bool, cancel: int = 0) -> Mesh:
    handle = first.engine.library.af_tissue_envelope(first.handle, second.handle, reverse, cancel)
    return owned(first.engine, handle)
