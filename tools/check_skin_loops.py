"""Quantify closed-guide parity, separating surface-edge normal ambiguity."""

import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import paths, skin_gaps, skin_loops
from anthroforge.native.mesh import GeometryEngine
from tools.check_skin_decimation import mesh


def curve(engine, points, closed=True):
    values = np.zeros((len(points), 11))
    values[:, :3], values[:, 9] = points, 1
    values[:, 3], values[:, 7] = 1, 1
    return paths.restore(engine, values, np.linspace(0, 1, len(points), endpoint=False), closed)


def evaluate(engine, row):
    surface = mesh(engine, np.array(row["vertices"]), np.array(row["faces"]))
    curves = [curve(engine, points) for points in row["paths"]]
    result = skin_loops.prepare(surface, curves, [np.eye(4)] * len(curves), [0, 0, 0, 1, 0, 0])
    return surface, curves, result


def supported_normal(engine, points, faces, normals, position, normal):
    selected = np.linalg.norm(normals - normal, axis=1) < 3e-6
    if not selected.any():
        return False
    scene = skin_gaps.create(engine, points, faces[selected], np.zeros(selected.sum()), [[0, 0, 0]])
    return bool(scene.sample([position], 1e6)[0, 0] < 3e-6)


def normal_ambiguities(engine, row, result):
    points, faces = np.array(row["vertices"]), np.array(row["faces"])
    normals = np.cross(
        points[faces[:, 1]] - points[faces[:, 0]], points[faces[:, 2]] - points[faces[:, 0]]
    )
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    current, expected = result.samples.reshape(-1, 6), np.array(row["normals"]).reshape(-1, 3)
    changed = np.flatnonzero(np.linalg.norm(current[:, 3:] - expected, axis=1) > 3e-6)
    for index in changed:
        for normal in (current[index, 3:], expected[index]):
            assert supported_normal(engine, points, faces, normals, current[index, :3], normal)
    return len(changed)


def check(engine, row):
    _, _, result = evaluate(engine, row)
    np.testing.assert_allclose(result.samples[:, :, :3], row["points"], atol=3e-6, rtol=0)
    np.testing.assert_array_equal(result.sources, row["sources"])
    np.testing.assert_array_equal(result.sources[result.pairs], row["pairs"])
    np.testing.assert_array_equal(result.symmetric, row["symmetric"])
    error = np.max(abs(result.samples[:, :, :3] - row["points"]))
    return dict(
        wavy=row["wavy"],
        shortened=row["shortened"],
        position_error=float(error),
        edge_normal_ambiguities=normal_ambiguities(engine, row, result),
        pairs=result.sources[result.pairs].tolist(),
        statuses=result.statuses.tolist(),
    )


def main():
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    engine = GeometryEngine()
    results = [check(engine, row) for row in data["cases"]]
    Path(sys.argv[2]).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
