"""Synchronous owned stacking sessions run only inside the application coordinator."""

import ctypes as c
from typing import Any

import numpy as np

from . import stacking_abi as abi
from .mesh import INT64, GeometryEngine, pointer


class StackSession:
    def __init__(self, engine: GeometryEngine) -> None:
        abi.configure(engine)
        self.engine, self.handle = engine, engine.library.af_stack_create()
        engine.check(not self.handle)

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_stack_release(self.handle)

    def run(self, domains: Any, settings: Any, **options: Any) -> Any:
        arguments, _leases = packed(domains, settings, **options)
        self.engine.check(self.engine.library.af_stack_run(self.handle, *arguments))
        return results(self)


def packed(
    domains: Any,
    settings: Any,
    policies: Any = (),
    regions: Any = (),
    obstacles: Any = (),
    cancel: int = 0,
) -> Any:
    rows = (abi.Domain * len(domains))(*domains)
    intent = (abi.Policy * len(policies))(*policies)
    faces = np.ascontiguousarray(regions, dtype=np.int64).reshape((-1, 2))
    bones = (abi.Obstacle * len(obstacles))(*obstacles)
    args: tuple[Any, ...] = (rows, len(rows), c.byref(settings), intent, len(intent))
    args += (faces.ctypes.data_as(INT64), len(faces), bones, len(bones), cancel)
    return args, faces


def results(session: StackSession) -> Any:
    engine, handle = session.engine, session.handle
    sizes = np.zeros(2, dtype=np.int64)
    engine.check(engine.library.af_stack_sizes(handle, sizes.ctypes.data_as(INT64)))
    output, orders = (abi.Output * int(sizes[0]))(), (abi.Order * int(sizes[1]))()
    engine.check(engine.library.af_stack_results(handle, output, len(output)))
    engine.check(engine.library.af_stack_orders(handle, orders, len(orders)))
    return {row.id: result(session, row) for row in output}, tuple(orders)


def result(session: StackSession, row: Any) -> dict[str, Any]:
    points, metrics = np.empty((row.vertices, 3)), np.zeros(24)
    session.engine.check(
        session.engine.library.af_stack_points(
            session.handle,
            row.id,
            pointer(points),
            row.vertices,
            pointer(metrics),
        )
    )
    return dict(status=row.status, message=row.message.decode(), points=points, metrics=metrics)
