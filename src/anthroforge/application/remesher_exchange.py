"""Validated mesh exchange shared by isolated remeshing backends."""

from pathlib import Path

from anthroforge.native import skin_topology
from anthroforge.native.mesh import GeometryEngine, Mesh


def write_triangles(path: Path, mesh: Mesh) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in mesh.array(0):
            stream.write("v " + " ".join(format(float(x), ".17g") for x in row) + "\n")
        for row in mesh.array(3):
            stream.write("f " + " ".join(str(int(x) + 1) for x in row) + "\n")


def read_mesh(engine: GeometryEngine, path: Path, arity: int, cancel: int) -> Mesh:
    return skin_topology.import_evaluated(engine, path, arity, cancel)
