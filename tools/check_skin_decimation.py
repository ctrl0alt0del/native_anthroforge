"""Compare native proxy decimation against captured Blender 5.0.1 meshes."""

import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

from anthroforge.native import skin_gaps, skin_proxy, topology
from anthroforge.native.mesh import GeometryEngine


def read(path):
    with path.open(encoding="utf-8") as source:
        vertices, faces = map(int, source.readline().split())
        points = np.array(
            [list(map(float, source.readline().split()))[:3] for _ in range(vertices)]
        )
        indices = np.array([list(map(int, source.readline().split())) for _ in range(faces)])
    return points, indices


def mesh(engine, points, faces):
    count = len(faces)
    return topology.restore(
        engine, [points, faces.ravel(), np.arange(count + 1) * 3, faces, np.arange(count)]
    )


def distances(engine, source, target):
    points = np.vstack([source[0], source[0][source[1]].mean(axis=1)])
    scene = skin_gaps.create(engine, *target, np.zeros(len(target[1])), [[0, 0, 0]])
    return scene.sample(points, 1e6)[:, 0]


def comparison(engine, first, second, scale):
    values = np.r_[distances(engine, first, second), distances(engine, second, first)] / scale
    return dict(p95=float(np.quantile(values, 0.95)), maximum=float(values.max()))


def qualify(engine, folder, name):
    source = read(folder / f"{name}-input.dat")
    expected = read(folder / f"{name}-blender.dat")
    original = mesh(engine, *source)
    start = perf_counter()
    result = skin_proxy.decimate(original, len(source[1]) // 4)
    seconds = perf_counter() - start
    np.testing.assert_array_equal(original.array(0), source[0])
    actual = result.array(0), result.array(3).astype(int)
    np.savez(folder / f"{name}-native.npz", points=actual[0], faces=actual[1])
    return report(engine, name, seconds, source, expected, actual)


def report(engine, name, seconds, source, expected, actual):
    scale = float(np.linalg.norm(np.ptp(source[0], axis=0)))
    return dict(
        name=name,
        faces=len(actual[1]),
        seconds=seconds,
        blender=comparison(engine, actual, expected, scale),
        source=comparison(engine, actual, source, scale),
    )


def main():
    folder = Path(sys.argv[1])
    names = sys.argv[2:] or ["sphere", "ellipsoid", "patch", "cube", "gap", "contact"]
    engine = GeometryEngine()
    results = [qualify(engine, folder, name) for name in names]
    (folder / "native-comparison.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
