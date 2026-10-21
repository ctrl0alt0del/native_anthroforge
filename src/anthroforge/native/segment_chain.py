"""Batch segment parameters into the native chain evaluator; no Python geometry loops."""

import ctypes as c

from anthroforge.core.segment_chain import SegmentChain

from .construction import owned_mesh
from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_segment_chain", [D, c.c_int, c.c_double, c.c_int, D, c.c_int, c.c_int, U], U)


def construct(engine: GeometryEngine, chain: SegmentChain, cancel: int) -> Mesh:
    records = doubles([(s.length, s.radius, s.bend, s.samples, s.sides) for s in chain.segments])
    profile = doubles(chain.profile)
    args = (
        pointer(records),
        len(records),
        chain.spread,
        chain.bend_mode == "CUMULATIVE",
        pointer(profile),
        len(profile) // 2,
        chain.unite,
        cancel,
    )
    return owned_mesh(engine, engine.library.af_segment_chain(*args))
