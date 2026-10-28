"""Capture original addon final diagnostics and budget voting on compact inputs."""

import hashlib
import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np


def shapes():
    plane = np.array([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]], float)
    cross = plane[:, [2, 0, 1]]
    quads = np.arange(8).reshape(2, 4)
    return [
        dict(name=name, vertices=np.vstack([plane, other]).tolist(), faces=quads.tolist())
        for name, other in (
            ("crossing", cross),
            ("contact", plane + [1, 0, 0]),
            ("separate", plane + [0, 0, 2]),
        )
    ]


def capture(row):
    from core import mesh_diagnostics

    points, faces = np.array(row["vertices"]), np.array(row["faces"])
    triangles = np.concatenate((faces[:, [0, 1, 2]], faces[:, [0, 2, 3]]))
    expected = mesh_diagnostics.intersections(points, triangles, budget=64 * 1024**2)
    samples = np.array([[0, 0, 0.1], [0.2, 0.1, -0.3], [2, 1, 0.4]])
    return row | dict(
        intersections=expected,
        samples=samples.tolist(),
        clearance=capture_clearance(points, faces, samples),
    )


def capture_clearance(points, faces, samples):
    from core.deformation import anatomy_quality

    reference = types.SimpleNamespace(arrays=dict(vertices=points, quads=faces, samples=samples))
    context = types.SimpleNamespace(
        deformation_reference=reference, anatomy_targets=samples + [0, 0.2, 0]
    )
    result = types.SimpleNamespace(
        vertices=points * [1, 1, 1.2], quads=faces, statistics=dict(warnings=[])
    )
    anatomy_quality.annotate(context, result)
    return result.statistics


def budgets(root):
    package = types.ModuleType("source_topology")
    package.__path__ = [str(root / "adapters/topology")]
    sys.modules[package.__name__] = package
    module = importlib.import_module(package.__name__ + ".density_runtime")
    owners = np.array([[2, 1, 2, 1], [-1, -1, 0, 1], [2, 2, 1, 0], [-1] * 4])
    faces = np.arange(owners.size).reshape(-1, 4)
    return dict(
        owners=owners.ravel().tolist(),
        faces=faces.tolist(),
        expected=module._face_owners(owners.ravel(), faces).tolist(),
    )


def main():
    root, destination = map(Path, sys.argv[1:])
    sys.path.insert(0, str(root))
    files = [
        "core/mesh_diagnostics.py",
        "core/deformation/anatomy_quality.py",
        "adapters/topology/density_runtime.py",
        "native/fiber_ccd/af_mesh_diagnostics.hpp",
    ]
    sources = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in files}
    data = dict(sources=sources, cases=[capture(row) for row in shapes()], budgets=budgets(root))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
