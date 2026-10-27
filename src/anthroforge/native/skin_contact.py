"""Pinned advisory contact projection and symmetry on fixed skin identities."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_fields import INT


class Input(c.Structure):
    _fields_ = [
        ("reference", D),
        ("current", D),
        ("proposed", D),
        ("count", c.c_int),
        ("faces", INT),
        ("face_count", c.c_int),
        ("symmetry", INT),
        ("plane", D),
        ("budget", U),
    ]


def configure(engine: Any) -> None:
    engine.bind("af_skin_contact", [c.POINTER(Input), D, D, U])
    engine.bind("af_skin_contact_symmetry", [D, c.c_int, D, INT, D, U])


def symmetry(engine: Any, points: Any, plane: Any, cancel: int = 0) -> tuple[Any, float]:
    points, plane = doubles(points), doubles(plane if plane is not None else np.zeros(6))
    if points.ndim != 2 or points.shape[1] != 3 or plane.shape != (6,):
        raise ValueError("Skin symmetry requires XYZ points and a six-value plane.")
    partners, maximum = np.full(len(points), -1, dtype=np.int32), np.zeros(1)
    if np.any(plane[3:]):
        source = pointer(points), len(points), pointer(plane)
        output = partners.ctypes.data_as(INT), pointer(maximum)
        engine.check(engine.library.af_skin_contact_symmetry(*source, *output, cancel))
    return partners, float(maximum[0])


def inputs(
    reference: Any, current: Any, proposed: Any, faces: Any, partners: Any, plane: Any
) -> Any:
    reference, current, proposed = (doubles(v) for v in (reference, current, proposed))
    faces, partners = (np.ascontiguousarray(v, dtype=np.int32) for v in (faces, partners))
    plane = doubles(plane if plane is not None else np.zeros(6))
    if reference.ndim != 2 or reference.shape[1] != 3:
        raise ValueError("Skin contact requires XYZ reference positions.")
    if current.shape != reference.shape or proposed.shape != reference.shape:
        raise ValueError("Skin contact must retain vertex identity and count.")
    validate_topology(faces, partners, plane, len(reference))
    return reference, current, proposed, faces, partners, plane


def validate_topology(faces: Any, partners: Any, plane: Any, count: int) -> None:
    valid_faces = faces.ndim == 2 and faces.shape[1] == 3
    if not valid_faces or partners.shape != (count,) or plane.shape != (6,):
        raise ValueError("Skin contact requires triangle faces and retained symmetry.")


def reference_inputs(arrays: Any, current: Any, proposed: Any) -> Any:
    topology = arrays["triangles"], arrays["symmetry_partners"], arrays["symmetry_plane"]
    return inputs(arrays["vertices"], current, proposed, *topology)


def evaluate(
    engine: Any, arrays: Any, current: Any, proposed: Any, budget: int, cancel: int = 0
) -> Any:
    data = reference_inputs(arrays, current, proposed)
    reference, current, proposed, faces, partners, plane = data
    points = pointer(reference), pointer(current), pointer(proposed), len(reference)
    topology = faces.ctypes.data_as(INT), len(faces), partners.ctypes.data_as(INT)
    value = Input(*points, *topology, pointer(plane), budget)
    output, report = np.empty_like(reference), np.zeros(8)
    engine.check(
        engine.library.af_skin_contact(c.byref(value), pointer(output), pointer(report), cancel)
    )
    return output, report
