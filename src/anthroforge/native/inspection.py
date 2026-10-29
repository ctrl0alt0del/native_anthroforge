"""Owned native inspection; no numerical work or live document access in adapters."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.entities import IDENTITY

from . import tissue_relaxation as relaxation
from .mesh import INT64, D, GeometryEngine, Mesh, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_inspection_compare", [U, U, c.c_int, D, U], U)
    engine.bind("af_inspection_release", [U], None)
    engine.bind("af_inspection_summary", [U, D, INT64])
    engine.bind("af_inspection_bytes", [U], U)
    engine.bind("af_inspection_point", [U, U, U, c.c_int, D, D, U])
    engine.bind("af_inspection_point_lines", [U, D, D, D])
    engine.bind("af_inspection_face_lines", [U, D, c.c_int, D])
    engine.bind("af_inspection_faces_lines", [U, D, INT64, c.c_int, D])
    configure_checks(engine)


def configure_checks(engine: GeometryEngine) -> None:
    from . import inspection_metrics, inspection_placement, inspection_volume

    inspection_metrics.configure(engine)
    inspection_placement.configure(engine)
    inspection_volume.configure(engine)
    engine.bind(
        "af_inspection_findings", [U, D, c.POINTER(U), D, c.c_int, c.c_int, INT64, D, INT64, U]
    )
    settings, region = c.POINTER(relaxation.Settings), c.POINTER(relaxation.Region)
    engine.bind("af_inspection_regions", [U, U, U, c.c_int, D, settings, region, c.c_int, D, U])


class Comparison:
    def __init__(
        self,
        reference: Mesh,
        target: Mesh,
        source: bool = False,
        cancel: int = 0,
        frame: Any = IDENTITY,
    ):
        self.engine, self.reference, self.target = target.engine, reference, target
        self.handle = self.engine.library.af_inspection_compare(
            reference.handle, target.handle, source, pointer(doubles(frame)), cancel
        )
        self.engine.check(not self.handle)
        self.read_summary()

    def read_summary(self) -> None:
        values, counts = (c.c_double * 10)(), (c.c_int64 * 2)()
        self.engine.check(self.engine.library.af_inspection_summary(self.handle, values, counts))
        self.stats, self.bounds, self.chunks, self.samples = (
            tuple(values[:4]),
            tuple(values[4:]),
            counts[0],
            counts[1],
        )

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_inspection_release(self.handle)

    @property
    def resources(self) -> tuple[Mesh, Mesh]:
        return self.reference, self.target

    @property
    def bytes(self) -> int:
        return int(self.engine.library.af_inspection_bytes(self.handle))


def point(
    mesh: Mesh,
    base: Mesh | None,
    triangle: int,
    bary: Any,
    rest: Mesh | None = None,
    cancel: int = 0,
    frame: Any = IDENTITY,
) -> dict[str, Any]:
    row = read_point(mesh, base, rest, triangle, bary, cancel)
    return dict(point_record(row, base is not None), glyph=point_lines(mesh, frame, row))


def read_point(
    mesh: Mesh, base: Mesh | None, rest: Mesh | None, triangle: int, bary: Any, cancel: int
) -> Any:
    weights, row = doubles(bary), np.zeros(20)
    if weights.shape != (3,):
        raise ValueError("An inspection point requires three triangle weights.")
    surfaces = mesh.handle, base.handle if base else 0, rest.handle if rest else 0
    mesh.engine.check(
        mesh.engine.library.af_inspection_point(
            *surfaces, triangle, pointer(weights), pointer(row), cancel
        )
    )
    return row


def point_lines(mesh: Mesh, frame: Any, row: Any) -> list[Any]:
    output, matrix = np.zeros((10, 3)), doubles(frame)
    mesh.engine.check(
        mesh.engine.library.af_inspection_point_lines(
            mesh.handle, pointer(matrix), pointer(row), pointer(output)
        )
    )
    return list(output.tolist())


def point_record(row: Any, base: bool) -> dict[str, Any]:
    record = dict(
        zip(
            ("position", "base_position", "displacement", "normal"),
            row[:12].reshape(4, 3).tolist(),
            strict=True,
        )
    )
    record.update(point_flags(row, base))
    return record


def point_flags(row: Any, base: bool) -> dict[str, Any]:
    return dict(
        part=int(row[12]),
        material_face=int(row[13]),
        side=int(row[14]),
        boundary=bool(row[15]),
        base_available=base,
        source_boundary=row[16],
        seam=row[17],
        zero_height=row[18],
        backing=row[19],
    )


def regions(
    mesh: Mesh, rest: Mesh, base: Mesh | None, triangle: int, bary: Any, item: Any, cancel: int
) -> Any:
    config, weights = relaxation.settings(item), doubles(bary)
    rows = (relaxation.Region * len(item.constraints))()
    fields, leases = {f.name: f for f in item.fields}, []
    for row, value in zip(rows, item.constraints, strict=True):
        leases.extend(relaxation.pack_region(row, value, fields))
    result = np.zeros((len(rows), 4))
    surfaces = mesh.handle, rest.handle, base.handle if base else 0
    query = triangle, pointer(weights), c.byref(config), rows, len(rows), pointer(result), cancel
    mesh.engine.check(mesh.engine.library.af_inspection_regions(*surfaces, *query))
    return result.tolist()


def findings(
    mesh: Mesh, frame: Any, others: list[Mesh], frames: Any, limit: int, cancel: int
) -> Any:
    if not 1 <= limit <= 4096:
        raise ValueError("Geometry finding limit must be between 1 and 4096.")
    handles = (U * len(others))(*(m.handle for m in others))
    ids, bounds, total = np.zeros((limit, 4), dtype=np.int64), np.zeros((limit, 6)), c.c_int64()
    world, transforms = doubles(frame), doubles(frames)
    inputs = mesh.handle, pointer(world), handles, pointer(transforms), len(others), limit
    outputs = ids.ctypes.data_as(INT64), pointer(bounds), c.byref(total), cancel
    mesh.engine.check(mesh.engine.library.af_inspection_findings(*inputs, *outputs))
    return ids[: total.value].tolist(), bounds[: total.value].tolist(), total.value == limit


def face_lines(mesh: Mesh, frame: Any, triangle: int) -> list[Any]:
    matrix, result = doubles(frame), np.zeros((6, 3))
    mesh.engine.check(
        mesh.engine.library.af_inspection_face_lines(
            mesh.handle, pointer(matrix), triangle, pointer(result)
        )
    )
    return list(result.tolist())


def faces_lines(mesh: Mesh, frame: Any, triangles: Any) -> list[Any]:
    indices = np.ascontiguousarray(triangles, dtype=np.int64)
    matrix, result = doubles(frame), np.empty((len(indices) * 6, 3))
    if indices.ndim != 1 or matrix.shape != (16,):
        raise ValueError("Invalid region outline dimensions.")
    mesh.engine.check(
        mesh.engine.library.af_inspection_faces_lines(
            mesh.handle,
            pointer(matrix),
            indices.ctypes.data_as(INT64),
            len(indices),
            pointer(result),
        )
    )
    return list(result.tolist())
