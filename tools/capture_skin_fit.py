"""Capture maintained addon Scale Aware and Single Active kernels without Blender UI."""

import ctypes as c
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np

P = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
INT = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")


def library(folder):
    directory = os.add_dll_directory(str(folder))
    lib = c.CDLL(str(folder / "af_bone_fit_v1.dll"))
    lib._directory = directory
    lib.db_error.restype = c.c_char_p
    prefix = [P, c.c_int, INT, c.c_int, P, c.c_int, c.c_int, c.c_int]
    lib.sb_fit.argtypes = prefix + [P, P]
    lib.one_fit.argtypes = prefix + [c.c_double, P, P, P]
    lib.sb_interpolate.argtypes = [P, P, c.c_int, c.c_double, P]
    lib.db_skin.argtypes = [P, c.c_int, P, c.c_int, P, P]
    return lib


def geometry():
    x = np.array([[i / 4, j / 2, 0.1 * (i / 4) ** 2] for j in range(3) for i in range(5)])
    q = np.array(
        [
            [j * 5 + i, j * 5 + i + 1, (j + 1) * 5 + i + 1, (j + 1) * 5 + i]
            for j in range(2)
            for i in range(4)
        ],
        np.int32,
    )
    return x, q


def pose(points, value):
    out = points.copy()
    angle = value * points[:, 0] * 0.5
    out[:, 0] = (1 + value * 0.25) * points[:, 0]
    out[:, 1] = points[:, 1] * np.cos(angle) - points[:, 2] * np.sin(angle)
    out[:, 2] = points[:, 1] * np.sin(angle) + points[:, 2] * np.cos(angle)
    return out


def prediction(lib, points, weights, matrices, keys, values):
    transforms, positions = [], []
    for value in values:
        right = min(int(np.searchsorted(keys, value, side="right")), len(keys) - 1)
        left = max(0, right - 1)
        t = float((value - keys[left]) / (keys[right] - keys[left]))
        matrix, result = np.empty_like(matrices[0]), np.empty_like(points)
        lib.sb_interpolate(matrices[left], matrices[right], weights.shape[1], t, matrix)
        lib.db_skin(points, len(points), weights, weights.shape[1], matrix, result)
        transforms.append(matrix.tolist())
        positions.append(result.tolist())
    return dict(matrices=transforms, positions=positions)


def fit(lib, points, quads, targets, single):
    bones = 2 if single else 3
    w, m = np.zeros((len(points), bones)), np.zeros((len(targets), bones, 4, 4))
    report = np.zeros(5)
    args = points, len(points), quads, len(quads), targets, len(targets)
    count = (
        (2 if lib.one_fit(*args, 0, 0, 0.0, w, m, report) else 0)
        if single
        else lib.sb_fit(*args, bones, 2, w, m)
    )
    if not count:
        raise RuntimeError(lib.db_error().decode())
    return np.ascontiguousarray(w[:, :count]), np.ascontiguousarray(m[:, :count])


def case(lib, single):
    points, quads = geometry()
    keys, values = np.array([0.0, 0.5, 1.0]), np.linspace(0, 1, 5)
    targets = np.array([pose(points, value) for value in keys])
    w, m = fit(lib, points, quads, targets, single)
    return dict(
        vertices=points.tolist(),
        quads=quads.tolist(),
        targets=targets.tolist(),
        keys=keys.tolist(),
        values=values.tolist(),
        weights=w.tolist(),
        training=m.tolist(),
        prediction=prediction(lib, points, w, m, keys, values),
    )


def main():
    folder, output = Path(sys.argv[1]), Path(sys.argv[2])
    lib = library(folder)
    hashes = {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in ("native.cpp", "af_bone_fit_v1.dll")
    }
    result = dict(
        provenance=dict(source=str(folder), sha256=hashes),
        cases={
            name: case(lib, single)
            for name, single in (("SCALE_AWARE", False), ("SINGLE_ACTIVE", True))
        },
    )
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
