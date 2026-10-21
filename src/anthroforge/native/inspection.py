"""Owned native inspection; no numerical work or live document access in adapters."""

import ctypes as c
from typing import Any

import numpy as np

from . import tissue_relaxation as relaxation
from anthroforge.core.entities import IDENTITY
from .mesh import D, INT64, U, GeometryEngine, Mesh, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_inspection_compare", [U, U, c.c_int, D, U], U)
    engine.bind("af_inspection_release", [U], None)
    engine.bind("af_inspection_summary", [U, D, INT64])
    engine.bind("af_inspection_bytes", [U], U)
    engine.bind("af_inspection_point", [U, U, c.c_int, D, D])
    engine.bind("af_inspection_face_lines", [U, D, c.c_int, D])
    configure_checks(engine)


def configure_checks(engine: GeometryEngine) -> None:
    engine.bind(
        "af_inspection_findings", [U, D, c.POINTER(U), D, c.c_int, c.c_int, INT64, D, INT64, U]
    )
    engine.bind(
        "af_inspection_regions",
        [U, U, U, c.c_int, D, c.POINTER(relaxation.Settings), c.POINTER(relaxation.Region), c.c_int, D, U],
    )


class Comparison:
    def __init__(self, reference: Mesh, target: Mesh, source: bool = False, cancel: int = 0, frame: Any = IDENTITY):
        self.engine, self.reference, self.target = target.engine, reference, target
        self.handle = self.engine.library.af_inspection_compare(reference.handle, target.handle, source, pointer(doubles(frame)), cancel)
        self.engine.check(not self.handle)
        values, counts = (c.c_double * 10)(), (c.c_int64 * 2)()
        self.engine.check(self.engine.library.af_inspection_summary(self.handle, values, counts))
        self.stats, self.bounds, self.chunks, self.samples = tuple(values[:4]), tuple(values[4:]), counts[0], counts[1]

    def __del__(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_inspection_release(self.handle)


def point(mesh: Mesh, base: Mesh | None, triangle: int, bary: Any) -> dict[str, Any]:
    weights, row = doubles(bary), np.zeros(20)
    if weights.shape != (3,):
        raise ValueError("An inspection point requires three triangle weights.")
    mesh.engine.check(mesh.engine.library.af_inspection_point(
        mesh.handle, base.handle if base else 0, triangle, pointer(weights), pointer(row)
    ))
    return dict(position=row[:3].tolist(), base_position=row[3:6].tolist(), displacement=row[6:9].tolist(),
                normal=row[9:12].tolist(), part=int(row[12]), material_face=int(row[13]),
                side=int(row[14]), boundary=bool(row[15]), base_available=base is not None,
                source_boundary=row[16], seam=row[17], zero_height=row[18], backing=row[19])


def regions(mesh: Mesh, rest: Mesh, base: Mesh | None, triangle: int, bary: Any, item: Any, cancel: int) -> Any:
    config, weights = relaxation.settings(item), doubles(bary)
    rows = (relaxation.Region * len(item.constraints))()
    fields, leases = {f.name: f for f in item.fields}, []
    for row, value in zip(rows, item.constraints, strict=True):
        leases.extend(relaxation.pack_region(row, value, fields))
    result = np.zeros((len(rows), 4))
    mesh.engine.check(mesh.engine.library.af_inspection_regions(
        mesh.handle, rest.handle, base.handle if base else 0, triangle, pointer(weights),
        c.byref(config), rows, len(rows), pointer(result), cancel
    ))
    return result.tolist()


def findings(mesh: Mesh, frame: Any, others: list[Mesh], frames: Any, limit: int, cancel: int) -> Any:
    if not 1 <= limit <= 4096:
        raise ValueError("Geometry finding limit must be between 1 and 4096.")
    handles = (U * len(others))(*(m.handle for m in others))
    ids, bounds, total = np.zeros((limit, 4), dtype=np.int64), np.zeros((limit, 6)), c.c_int64()
    world, transforms = doubles(frame), doubles(frames)
    mesh.engine.check(mesh.engine.library.af_inspection_findings(
        mesh.handle, pointer(world), handles, pointer(transforms), len(others), limit,
        ids.ctypes.data_as(INT64), pointer(bounds), c.byref(total), cancel
    ))
    return ids[:total.value].tolist(), bounds[:total.value].tolist(), total.value == limit


def face_lines(mesh: Mesh, frame: Any, triangle: int) -> list[Any]:
    matrix, result = doubles(frame), np.zeros((6, 3))
    mesh.engine.check(mesh.engine.library.af_inspection_face_lines(
        mesh.handle, pointer(matrix), triangle, pointer(result)
    ))
    return result.tolist()
