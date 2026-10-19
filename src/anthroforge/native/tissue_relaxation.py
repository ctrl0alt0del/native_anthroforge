"""Owned native relaxation calls, without Python geometry assembly or solver loops."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.tissue_diagnostics import TissueDiagnostic

from .mesh import D, GeometryEngine, Mesh, U, pointer
from .tissue_shapes import owned

MASKS = {
    name: i for i, name in enumerate(("ALL", "BACKING", "BOUNDARY", "ENDPOINTS", "SUSPENSION"))
}
PARAMETERS = dict(
    sagginess="sagginess",
    limit="sag_limit",
    shape="shape_retention",
    volume="volume_retention",
    slack="slack",
    tolerance="tolerance",
)


class Source(c.Structure):
    _fields_ = [(name, U) for name in ("mesh", "path", "host")]
    _fields_ += [(name, c.c_double * 16) for name in ("frame", "host_frame")]


class Settings(c.Structure):
    _fields_ = [(name, c.c_int) for name in ("mode", "iterations", "passes")]
    _fields_ += [("gravity", c.c_double * 3)]
    _fields_ += [
        (name, c.c_double)
        for name in (
            "sagginess",
            "limit",
            "shape",
            "volume",
            "slack",
            "tolerance",
            "amount",
            "minimum",
            "power",
        )
    ]


class Region(c.Structure):
    _fields_ = [(name, c.c_int) for name in ("mask", "mode", "domain")]
    _fields_ += [(name, c.c_double) for name in ("strength", "feather", "offset")]
    _fields_ += [("weights", D), ("count", c.c_int64), ("goals", D)]


def configure(engine: GeometryEngine) -> None:
    engine.bind(
        "af_tissue_relax",
        [U, c.POINTER(Source), c.POINTER(Settings), c.POINTER(Region), c.c_int, D, U],
        U,
    )


def settings(item: Any) -> Settings:
    s, inflation = item.relaxation, item.parts[0].a.inflation
    result = Settings(
        ("NONE", "GEOMETRIC", "STATIC_PBD").index(s.mode), s.iterations, s.constraint_passes
    )
    result.gravity[:] = s.gravity
    for key, name in PARAMETERS.items():
        setattr(result, key, getattr(s, name))
    for key in ("amount", "minimum", "power"):
        setattr(result, key, getattr(inflation, key))
    return result


def regions(item: Any) -> tuple[Any, list[Any]]:
    rows, buffers = (Region * len(item.constraints))(), []
    fields = {f.name: f for f in item.fields}
    for row, value in zip(rows, item.constraints, strict=True):
        buffers.extend(pack_region(row, value, fields))
    return rows, buffers


def pack_region(row: Region, value: Any, fields: Any) -> list[Any]:
    row.mask, row.mode = MASKS.get(value.mask, 5), int(value.mode == "SOFT")
    row.strength, row.feather, row.offset = value.strength, value.feather, value.offset
    if value.reference is not None:
        raise ValueError("Target-relative constraint bindings must be resolved before evaluation.")
    if row.mask != 5:
        return []
    field = fields[value.mask]
    buffer = np.ascontiguousarray(field.values, dtype=np.float64)
    row.weights, row.count, row.domain = pointer(buffer), len(buffer), int(field.domain == "REST")
    return [buffer]


def evaluate(
    mesh: Mesh, source: Source, item: Any, cancel: int = 0
) -> tuple[Mesh, TissueDiagnostic]:
    config, (rows, _leases), report = settings(item), regions(item), np.zeros(7)
    handle = mesh.engine.library.af_tissue_relax(
        mesh.handle, c.byref(source), c.byref(config), rows, len(rows), pointer(report), cancel
    )
    output = owned(mesh.engine, handle)
    return output, diagnostic(report)


def diagnostic(report: Any) -> TissueDiagnostic:
    states = ("NOT_APPLICABLE", "CONVERGED", "ITERATION_LIMIT")
    return TissueDiagnostic(
        "intrinsic", states[int(report[0])], int(report[1]), *map(float, report[2:])
    )
