"""Capture original contact diagnostics/correction without foreground Blender."""

import ctypes as c
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from capture_skin_deformation import INT, P, library


def configure(lib):
    geometry = [P, P, P, c.c_int, INT, c.c_int, INT, P]
    lib.af_ad_contact.argtypes = geometry + [c.c_uint64, c.c_char_p, P, P]
    lib.af_ad_symmetry.argtypes = [P, c.c_int, P, INT, P]


def inputs():
    points = np.array(
        [[-1, -1, -0.2], [1, -1, -0.2], [0, 1, -0.2], [-1, -1, 0.2], [1, -1, 0.2], [0, 1, 0.2]]
    )
    faces = np.array([[0, 1, 2], [3, 4, 5]], np.int32)
    return points, faces


def symmetry(lib, points, plane):
    partners, maximum = np.empty(len(points), np.int32), np.zeros(1)
    if not lib.af_ad_symmetry(points, len(points), plane, partners, maximum):
        raise RuntimeError(lib.af_ad_error().decode())
    return partners, float(maximum[0])


def solve(lib, reference, current, proposed, faces, partners, plane):
    out, stats = np.empty_like(reference), np.zeros(8)
    geometry = reference, current, proposed, len(reference), faces, len(faces), partners, plane
    if not lib.af_ad_contact(*geometry, 1 << 30, b"", out, stats):
        raise RuntimeError(lib.af_ad_error().decode())
    return dict(points=out.tolist(), diagnostics=stats.tolist())


def cases(lib):
    points, faces = inputs()
    plane = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    partners, error = symmetry(lib, points, plane)
    rows = solve_cases(lib, points, faces, partners, plane)
    return dict(
        vertices=points.tolist(),
        triangles=faces.tolist(),
        symmetry_plane=plane.tolist(),
        symmetry_partners=partners.tolist(),
        symmetry_error=error,
        cases=rows,
    )


def solve_cases(lib, points, faces, partners, plane):
    cross = points.copy()
    cross[:, 2] *= -1
    requests = dict(identity=(points, points), crossing=(points, cross), reopening=(cross, points))
    return {
        name: dict(
            current=a.tolist(),
            proposed=b.tolist(),
            result=solve(lib, points, a, b, faces, partners, plane),
        )
        for name, (a, b) in requests.items()
    }


def main(root, output):
    lib = library(root)
    configure(lib)
    files = ("af_deformation_v1.dll", "contact.hpp", "contact_geometry.hpp")
    hashes = {
        name: hashlib.sha256((root / "native/deformation" / name).read_bytes()).hexdigest()
        for name in files
    }
    output.write_text(json.dumps(dict(source=hashes, **cases(lib)), indent=2) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
