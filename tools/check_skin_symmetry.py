"""Compare source-backed symmetry by positions and oriented material triangles/quads."""

import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import skin_symmetry
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_assembly import quads
from tools.check_skin_decimation import mesh


def evaluate(engine, row):
    points, faces = np.array(row["vertices"]), np.array(row["faces"])
    source = (quads if row["operation"] == "mirror" else mesh)(engine, points, faces)
    if row["operation"] == "half":
        return source, skin_symmetry.half(source, row["plane"])
    return source, skin_symmetry.mirror(source, row["plane"]).mesh


def oriented(faces):
    return {min(tuple(np.roll(face, i)) for i in range(len(face))) for face in faces}


def correspondence(actual, expected):
    distances = np.linalg.norm(expected[:, None] - actual, axis=2)
    error = max(distances.min(0).max(), distances.min(1).max())
    return float(error), distances.argmin(1)


def compare(mesh, row):
    points, faces = np.array(row["expected"]["points"]), np.array(row["expected"]["faces"])
    error, mapping = correspondence(mesh.array(0), points)
    mapped = mapping[faces]
    valid = np.array([len(set(face)) == len(face) for face in mapped])
    actual = mesh.array(1).reshape(-1, faces.shape[1])
    return dict(
        name=row["name"],
        error=error,
        connectivity=oriented(actual) == oriented(mapped[valid]),
        degenerate_source_faces=int(np.sum(~valid)),
        faces=len(actual),
    )


def main():
    rows = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["cases"]
    engine = GeometryEngine()
    results = [compare(evaluate(engine, row)[1], row) for row in rows]
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
