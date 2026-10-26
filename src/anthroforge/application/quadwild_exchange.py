"""Validated remesher exchange; numerical preparation remains in native adapters."""

from pathlib import Path
from typing import Any

import numpy as np

from anthroforge.native.mesh import GeometryEngine, Mesh


def write_triangles(path: Path, mesh: Mesh) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in mesh.array(0):
            stream.write("v " + " ".join(format(float(x), ".17g") for x in row) + "\n")
        for row in mesh.array(3):
            stream.write("f " + " ".join(str(int(x) + 1) for x in row) + "\n")


def read_mesh(engine: GeometryEngine, path: Path, arity: int, cancel: int) -> Mesh:
    mesh = engine.import_mesh(path, 1.0, False, cancel)
    if not mesh.counts[1] or np.any(np.diff(mesh.array(2)) != arity):
        raise ValueError(f"QuadWild must produce nonempty {arity}-sided polygons.")
    return mesh


def read_field(path: Path, count: int) -> Any:
    values = np.loadtxt(path, skiprows=2, ndmin=2)
    if values.shape != (count, 3) or not np.isfinite(values).all():
        raise ValueError("QuadWild prior field does not match its triangle mesh.")
    return values


def write_field(path: Path, values: Any) -> None:
    np.savetxt(path, values, header=f"{len(values)}\n4", comments="")


def write_features(path: Path, values: Any) -> None:
    np.savetxt(path, values, fmt="%d", delimiter=",", header=str(len(values)), comments="")
