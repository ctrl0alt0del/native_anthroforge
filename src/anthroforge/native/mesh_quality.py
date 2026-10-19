"""Native geometric diagnostics; large normal rotations are not proof of inversion."""

import ctypes as c
from dataclasses import dataclass

from .mesh import INT64, GeometryEngine, Mesh, U


@dataclass(frozen=True)
class DeformationQuality:
    baseline_crossings: int
    new_crossings: int
    new_collapses: int
    normal_rotations: int


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_mesh_deformation_quality", [U, U, INT64, U])
    engine.bind("af_mesh_validate_deformation", [U, U, U])


def deformation(rest: Mesh, result: Mesh, cancel: int = 0) -> DeformationQuality:
    counts = (c.c_int64 * 4)()
    rest.engine.check(
        rest.engine.library.af_mesh_deformation_quality(rest.handle, result.handle, counts, cancel)
    )
    return DeformationQuality(*counts)


def validate(rest: Mesh, result: Mesh, cancel: int = 0) -> None:
    rest.engine.check(
        rest.engine.library.af_mesh_validate_deformation(rest.handle, result.handle, cancel)
    )
