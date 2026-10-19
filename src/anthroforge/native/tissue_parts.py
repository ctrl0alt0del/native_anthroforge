"""Batch independent per-part inflation settings into the shared native assembly."""

import ctypes as c
from typing import Any

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer
from .tissue_inflation import Inflation, pack
from .tissue_shapes import owned


def configure(engine: GeometryEngine) -> None:
    from . import tissue_smoothing

    tissue_smoothing.configure(engine)
    engine.bind("af_tissue_inflate_parts", [U, c.POINTER(Inflation), c.c_int, D, c.c_int, U], U)
    engine.bind("af_tissue_envelope", [U, U, c.c_int, U], U)
    engine.bind("af_tissue_profile_reset", [c.c_double, D])
    engine.bind("af_tissue_control_default", [U, c.c_int, D])


def evaluate(
    mesh: Mesh, parts: Any, side: str, reverse: bool, cancel: int = 0, envelope: bool = False
) -> Mesh:
    settings = (Inflation * len(parts))(*(pack(getattr(p, side).inflation, reverse) for p in parts))
    connectors = doubles([(p.connector_width, p.connector_fullness) for p in parts])
    handle = mesh.engine.library.af_tissue_inflate_parts(
        mesh.handle, settings, len(parts), pointer(connectors), envelope, cancel
    )
    return owned(mesh.engine, handle)


def compose(first: Mesh, second: Mesh, reverse: bool, cancel: int = 0) -> Mesh:
    handle = first.engine.library.af_tissue_envelope(first.handle, second.handle, reverse, cancel)
    return owned(first.engine, handle)


def reset_profile(engine: GeometryEngine, depth: float) -> tuple[float, ...]:
    output = (c.c_double * 9)()
    engine.check(engine.library.af_tissue_profile_reset(depth, output))
    return tuple(output)


def default_control(mesh: Mesh, part: int) -> tuple[float, ...]:
    output = (c.c_double * 3)()
    mesh.engine.check(mesh.engine.library.af_tissue_control_default(mesh.handle, part, output))
    return tuple(output)
