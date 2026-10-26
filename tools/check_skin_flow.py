"""Compare the standalone FLOW kernel directly with the original addon DLL."""

import ctypes as c
import json
import sys
from pathlib import Path

import numpy as np

from anthroforge.native import skin_flow
from anthroforge.native.mesh import GeometryEngine


def fixture(engine, angle):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tests.test_skin_flow import fixture as make

    return make(engine, angle)


def configure(library):
    p = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
    i = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    library.af_field.argtypes = [p, i, c.c_int, p, p, p, p, i, c.c_int, c.c_double, c.c_int, p, p]


def baseline(library, mesh, prior, samples):
    output, information = np.empty_like(prior), np.empty_like(prior)
    values = [np.ascontiguousarray(samples[:, k : k + 3]) for k in (0, 3, 6)]
    owners = np.ascontiguousarray(samples[:, 9], dtype=np.int32)
    vertices, triangles = mesh.array(0).copy(), mesh.array(3).copy()
    radius = max(float(np.ptp(vertices, axis=0).max()) * 0.035, 1e-10)
    inputs = vertices, triangles, len(triangles), prior, *values, owners, len(samples), radius, 1
    assert library.af_field(*inputs, output, information)
    return output, information


def compare(library, engine, angle, empty=False):
    mesh, prior, samples = fixture(engine, angle)
    if empty:
        samples = np.empty((0, 10))
    expected = baseline(library, mesh, prior, samples)
    actual = skin_flow.solve(mesh, prior, samples)
    for first, second in zip(expected, actual, strict=True):
        np.testing.assert_allclose(first, second, atol=1e-12, rtol=1e-12)
    return dict(
        angle=angle,
        empty=empty,
        maximum_error=max(
            float(np.max(np.abs(a - b))) for a, b in zip(expected, actual, strict=True)
        ),
    )


def path_baseline(library, mesh, points):
    p = np.ctypeslib.ndpointer(np.float64, flags="C_CONTIGUOUS")
    i = np.ctypeslib.ndpointer(np.int32, flags="C_CONTIGUOUS")
    library.af_path.argtypes = [p, c.c_int, i, c.c_int, p, c.c_int, i, c.c_int]
    output = np.empty(mesh.counts[3] * 6, dtype=np.int32)
    geometry = mesh.array(0), mesh.counts[0], mesh.array(3), mesh.counts[3]
    count = library.af_path(*geometry, points, len(points), output, len(output))
    assert count >= 0
    return output[: count * 2].reshape(-1, 2)


def paths(library, engine):
    mesh, _, _ = fixture(engine, 0.0)
    points = np.array([[0, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float)
    expected = path_baseline(library, mesh, points)
    actual = skin_flow.route(mesh, points)
    np.testing.assert_array_equal(actual, expected)
    return dict(feature_edges=actual.tolist(), exact=True)


def main():
    library = c.CDLL(str(Path(sys.argv[1]) / "native/topology/af_topology_field_v1.dll"))
    configure(library)
    engine = GeometryEngine()
    results = [
        compare(library, engine, angle, empty)
        for angle, empty in ((0.4, False), (-0.6, False), (1.2, False), (0.0, True))
    ]
    results.append(paths(library, engine))
    path = Path("build/skin-040/flow-parity.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
