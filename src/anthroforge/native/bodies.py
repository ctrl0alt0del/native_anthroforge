"""Body bases and curve deformation are separate native evaluation stages."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import BodyPiece, Curve

from .construction import curve_records, owned_mesh
from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    from .geometry_modifiers import configure as configure_modifiers

    configure_modifiers(engine)
    from .segment_chain import configure as configure_chain

    configure_chain(engine)
    engine.bind("af_curve_path", [D, c.c_int, c.c_int, c.c_int, D, c.POINTER(c.c_int), U])
    base_args = [c.c_int, c.c_int, c.c_int, c.c_double, c.c_double, c.c_double, c.c_int, U]
    engine.bind("af_body_base", base_args, U)
    engine.bind("af_body_base_geometry", base_args, U)
    engine.bind("af_curve_deform", [U, D, c.c_int, c.c_int, c.c_double, c.c_double, c.c_int, U], U)


def path(engine: GeometryEngine, curve: Curve, cancel: int, records: Any = None) -> Any:
    data = curve_records(curve) if records is None else doubles(records)
    output, count = np.empty((len(curve.points) * curve.resolution + 1, 11)), c.c_int()
    args = (
        pointer(data),
        len(data),
        curve.closed,
        curve.resolution,
        pointer(output),
        c.byref(count),
        cancel,
    )
    engine.check(engine.library.af_curve_path(*args))
    return output[: count.value]


def base(engine: GeometryEngine, piece: BodyPiece, count: int, closed: bool, cancel: int) -> Mesh:
    return owned_mesh(engine, engine.library.af_body_base(*base_key(piece, count, closed), cancel))


def base_key(piece: BodyPiece, count: int, closed: bool) -> tuple[Any, ...]:
    shape = ("BOX", "CYLINDER", "CAPSULE").index(piece.shape)
    return (
        max(3, count),
        shape,
        piece.sides,
        piece.width,
        piece.depth,
        piece.length,
        closed,
    )


def draft_base(
    engine: GeometryEngine, piece: BodyPiece, count: int, closed: bool, cancel: int
) -> Mesh:
    key = base_key(piece, count, closed)
    cached = engine.bases.get(key)
    if cached is not None:
        return cached
    mesh = owned_mesh(engine, engine.library.af_body_base_geometry(*key, cancel))
    return engine.bases.put(key, mesh)


def bend(mesh: Mesh, samples: Any, piece: BodyPiece, closed: bool, cancel: int) -> Mesh:
    data = doubles(samples)
    args = (
        mesh.handle,
        pointer(data),
        len(data),
        piece.fit,
        piece.length,
        piece.position,
        closed,
        cancel,
    )
    return owned_mesh(mesh.engine, mesh.engine.library.af_curve_deform(*args))
