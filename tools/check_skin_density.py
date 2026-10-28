"""Direct addon comparison for the migrated density arithmetic and iterative correction."""

import importlib
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
from check_skin_quadwild import addon

from anthroforge.native import skin_density, topology
from anthroforge.native.mesh import GeometryEngine


def grid(engine, size=40):
    x, y = np.meshgrid(np.linspace(0, 1, size), np.linspace(0, 1, size))
    vertices = np.column_stack((x.ravel(), y.ravel(), np.zeros(x.size)))
    ids = np.arange(size * size).reshape(size, size)
    a, b, c, d = (v.ravel() for v in (ids[:-1, :-1], ids[:-1, 1:], ids[1:, 1:], ids[1:, :-1]))
    faces = np.vstack((np.column_stack((a, b, c)), np.column_stack((a, c, d)))).astype(np.int32)
    arrays = [vertices, faces.ravel(), np.arange(len(faces) + 1) * 3, faces, np.arange(len(faces))]
    return topology.restore(engine, arrays), (vertices[:, 0] >= 0.5).astype(np.int32)


def baseline(mesh, labels, targets):
    budgets = importlib.import_module("addon_reference.core.topology.budgets")
    ownership = importlib.import_module("addon_reference.core.topology.ownership")
    model = importlib.import_module("addon_reference.core.topology.model")
    areas = ownership.vertex_areas(mesh.array(0), mesh.array(3))
    regions = baseline_regions(model, labels, areas, targets)
    field = budgets.density_field(regions, len(labels))
    lengths = budgets.smooth_target_lengths(
        field.target_edge_lengths, mesh.array(3), areas, regions
    )
    return lengths, areas, [row.area for row in regions]


def baseline_regions(model, labels, areas, targets):
    return [
        model.TopologyBudgetRegion(
            str(i), n, n, tuple(np.flatnonzero(labels == i)), float(areas[labels == i].sum())
        )
        for i, n in enumerate(targets)
    ]


def compare(mesh, labels, targets):
    start = perf_counter()
    expected = baseline(mesh, labels, targets)
    addon_seconds = perf_counter() - start
    start = perf_counter()
    actual = skin_density.evaluate(mesh, labels, targets)
    native_seconds = perf_counter() - start
    for a, b in zip((actual.lengths, actual.areas, actual.region_areas), expected, strict=True):
        np.testing.assert_allclose(a, b, atol=1e-12, rtol=1e-12)
    return dict(
        budgets=targets,
        maximum_length_error=float(np.max(np.abs(actual.lengths - expected[0]))),
        addon_seconds=addon_seconds,
        native_seconds=native_seconds,
    )


def main():
    addon(Path(sys.argv[1]))
    mesh, labels = grid(GeometryEngine())
    report = [compare(mesh, labels, targets) for targets in ([100, 400], [0, 400], [0, 0, 100])]
    path = Path("build/skin-040/density-parity.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
