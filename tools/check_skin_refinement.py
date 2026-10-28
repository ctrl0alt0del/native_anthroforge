"""Compare native quad split/proximity preparation to the maintained addon kernels."""

import importlib
import json
import sys
import types
from pathlib import Path
from time import perf_counter

import numpy as np
from check_skin_quadwild import addon

from anthroforge.native import skin_ownership, skin_proximity, skin_topology
from anthroforge.native.mesh import GeometryEngine


def reference(root):
    addon(root)
    for suffix in ("adapters", "adapters.topology"):
        name = "addon_reference." + suffix
        package = types.ModuleType(name)
        package.__path__ = [str(root.joinpath(*suffix.split(".")))]
        sys.modules[name] = package
    return importlib.import_module("addon_reference.core.topology.refine")


def split_parity(mesh, algorithm):
    faces = mesh.array(1).reshape(-1, 4)
    for bits in range(1 << len(faces)):
        mask = np.array([(bits >> i) & 1 for i in range(len(faces))], dtype=bool)
        vertices, quads, parents = algorithm.refine_quads(mesh.array(0), faces, mask)
        actual = skin_topology.split(mesh, mask, guides=np.arange(len(faces)))
        np.testing.assert_allclose(actual.mesh.array(0), vertices, atol=1e-14, rtol=0)
        np.testing.assert_array_equal(actual.mesh.array(1).reshape(-1, 4), quads)
        np.testing.assert_array_equal(actual.guides, parents)
    return dict(split_patterns=1 << len(faces), maximum_coordinate_tolerance=1e-14)


def adaptive_inputs(mesh, target, plane):
    points, faces = mesh.array(0), mesh.array(1).reshape(-1, 4)
    lengths = np.linspace(0.12, 0.47, len(points))
    frame = None if plane is None else types.SimpleNamespace(origin=plane[:3], normal=plane[3:])
    capture = types.SimpleNamespace(
        vertices=points, plane=frame, settings=types.SimpleNamespace(target_quad_count=target)
    )
    labels, guides = np.zeros(len(faces), dtype=np.int32), np.arange(len(faces), dtype=np.int32)
    return capture, (points, faces, labels, guides), lengths


def adaptive_parity(mesh, target, plane=None):
    algorithm = importlib.import_module("addon_reference.adapters.topology.adaptive_refine")
    capture, data, lengths = adaptive_inputs(mesh, target, plane)
    start = perf_counter()
    expected = algorithm.refine_to_density(
        capture, data, (np.zeros(len(lengths), dtype=np.int32), lengths)
    )
    addon_seconds = perf_counter() - start
    start = perf_counter()
    result = skin_topology.refine(mesh, mesh, lengths, target, data[2], data[3], plane)
    seconds = perf_counter() - start
    assert_result(result, expected)
    return adaptive_report(result, target, addon_seconds, seconds)


def adaptive_report(result, target, addon_seconds, seconds):
    return dict(
        target=target,
        quads=result.mesh.counts[1],
        addon_seconds=addon_seconds,
        native_seconds=seconds,
    )


def assert_result(result, expected):
    actual = (
        result.mesh.array(0),
        result.mesh.array(1).reshape(-1, 4),
        result.regions,
        result.guides,
    )
    for first, second in zip(actual, expected, strict=True):
        np.testing.assert_allclose(first, second, atol=1e-14, rtol=0)


def proximity_parity(mesh):
    algorithm = importlib.import_module("addon_reference.core.topology.refinement")
    points = mesh.array(0)
    source = sample_cloud(points + [0, 0, 0.07])
    packed = skin_ownership.pack(source, [0, len(points)], [-1], [[]])
    lengths = np.linspace(0.1, 0.5, len(points))
    result = skin_proximity.evaluate(mesh, packed, [1], lengths)
    weights = algorithm.muscle_proximity_weights(
        np.full(len(points), 0.07), np.linalg.norm(np.ptp(points, axis=0))
    )
    np.testing.assert_allclose(result.weights, weights, atol=1e-14, rtol=0)
    np.testing.assert_allclose(
        result.lengths, algorithm.muscle_target_lengths(lengths, weights), atol=1e-14, rtol=0
    )
    return dict(maximum_weight_error=float(np.max(abs(result.weights - weights))))


def sample_cloud(points):
    from anthroforge.native.skin_capture import Capture

    return Capture(
        points,
        np.empty((0, 3), dtype=np.int64),
        np.empty(0, dtype=np.int32),
        np.empty(0),
        np.empty((1, 3)),
    )


def fixtures(engine):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tests.test_skin_refinement import grid

    return grid(engine), grid(engine, 10, 8)


def main():
    algorithm = reference(Path(sys.argv[1]))
    engine = GeometryEngine()
    small, large = fixtures(engine)
    report = dict(split=split_parity(small, algorithm), proximity=proximity_parity(small))
    report["adaptive"] = [adaptive_parity(large, target) for target in (100, 160, 300)]
    report["symmetry"] = adaptive_parity(small, 24, [1.5, 0, 0, 1, 0, 0])
    path = Path("build/skin-040/refinement-parity.json")
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
