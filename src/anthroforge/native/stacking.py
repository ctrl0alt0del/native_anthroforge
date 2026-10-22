"""Synchronous owned stacking sessions run only inside the application coordinator."""

import ctypes as c
from typing import Any

import numpy as np

from . import stacking_abi as abi
from .mesh import INT64, GeometryEngine, U, pointer


class StackSession:
    def __init__(self, engine: GeometryEngine) -> None:
        abi.configure(engine)
        self.engine, self.handle = engine, engine.library.af_stack_create()
        engine.check(not self.handle)
        if engine.resource_observer is not None:
            engine.resource_observer(self)

    @property
    def bytes(self) -> int:
        return int(self.engine.library.af_stack_bytes(self.handle))

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_stack_release(self.handle)

    def run(self, domains: Any, settings: Any, **options: Any) -> Any:
        arguments, _leases = packed(domains, settings, **options)
        self.engine.check(self.engine.library.af_stack_run(self.handle, *arguments))
        return results(self)

    def plan(self, domains: Any, settings: Any, metadata_only: bool = False, **options: Any) -> Any:
        arguments, _leases = packed(domains, settings, **options)
        self.engine.check(self.engine.library.af_stack_plan(self.handle, *arguments))
        return results(self, metadata_only)

    def resolve(self, accepted: Any, targets: Any, cancel: int = 0) -> Any:
        rows, _leases = accepted_rows(accepted)
        selected = (U * len(targets))(*targets)
        self.engine.check(
            self.engine.library.af_stack_resolve(
                self.handle, rows, len(rows), selected, len(selected), cancel
            )
        )
        return results(self)

    def validate_surfaces(self, surfaces: Any, cancel: int = 0) -> None:
        rows = (abi.Surface * len(surfaces))(*surfaces)
        self.engine.check(
            self.engine.library.af_stack_validate_surfaces(self.handle, rows, len(rows), cancel)
        )


def surface(intrinsic: Any, final: Any, frame: Any, changed: bool = True) -> Any:
    row = abi.Surface(intrinsic=intrinsic.handle, final=final.handle, changed=changed)
    row.frame[:] = frame
    return row


def resolve_group(engine: Any, targets: Any, accepted: Any, cancel: int = 0) -> Any:
    rows, _leases = accepted_rows(accepted)
    selected = (abi.Target * len(targets))(
        *(abi.Target(session.handle, key) for key, session in targets.items())
    )
    engine.check(
        engine.library.af_stack_resolve_group(selected, len(selected), rows, len(rows), cancel)
    )
    return {
        key: result(session, output)
        for key, session in targets.items()
        for output in output_rows(session)
        if output.id == key
    }


def output_rows(session: StackSession) -> Any:
    size = np.zeros(2, dtype=np.int64)
    session.engine.check(
        session.engine.library.af_stack_sizes(session.handle, size.ctypes.data_as(INT64))
    )
    rows = (abi.Output * int(size[0]))()
    session.engine.check(session.engine.library.af_stack_results(session.handle, rows, len(rows)))
    return rows


def accepted_rows(accepted: Any) -> Any:
    arrays = [np.ascontiguousarray(row["points"], dtype=np.float64) for row in accepted.values()]
    for points in arrays:
        if points.ndim != 2 or points.shape[1] != 3:
            raise ValueError("Accepted stacking points must be an N by 3 array.")
    rows = [
        abi.Accepted(key, pointer(points), len(points), row["status"])
        for (key, row), points in zip(accepted.items(), arrays, strict=True)
    ]
    return (abi.Accepted * len(rows))(*rows), arrays


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


def results(session: StackSession, metadata_only: bool = False) -> Any:
    engine, handle = session.engine, session.handle
    sizes = np.zeros(2, dtype=np.int64)
    engine.check(engine.library.af_stack_sizes(handle, sizes.ctypes.data_as(INT64)))
    output, orders = (abi.Output * int(sizes[0]))(), (abi.Order * int(sizes[1]))()
    engine.check(engine.library.af_stack_results(handle, output, len(output)))
    engine.check(engine.library.af_stack_orders(handle, orders, len(orders)))
    return {
        row.id: dict(status=row.status, message=row.message.decode())
        if metadata_only
        else result(session, row)
        for row in output
    }, tuple(orders)


def dependencies(session: StackSession) -> tuple[tuple[int, int], ...]:
    library, handle = session.engine.library, session.handle
    size = library.af_stack_dependencies(handle, None, 0)
    session.engine.check(size < 0)
    values = (U * (2 * size))()
    session.engine.check(library.af_stack_dependencies(handle, values, size) < 0)
    return tuple((values[2 * i], values[2 * i + 1]) for i in range(size))


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
