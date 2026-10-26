"""Direct addon attribution parity on compact meshes; mirrored correction is tested separately."""

import importlib
import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np
from check_skin_density import grid
from check_skin_quadwild import addon

from anthroforge.native import skin_capture, skin_ownership
from anthroforge.native.mesh import GeometryEngine


def sources(engine):
    positions = ([0.1, 0.2, -0.1], [0.85, 0.7, -0.1], [0.65, 0.4, -0.02])
    shape = np.array([[0, 0, 0], [0.1, 0, 0], [0, 0.1, 0]])
    return [engine.create_mesh(shape + p, [0, 1, 2], [0, 3]) for p in positions]


def baseline(mesh, inputs):
    model = importlib.import_module("addon_reference.core.topology.model")
    algorithm = importlib.import_module("addon_reference.core.topology.ownership")
    rows = tuple(baseline_source(model, i, value) for i, value in enumerate(inputs))
    rules = tuple(model.TopologyDensityRule(i, str(i), "", "INHERIT", 0) for i in range(2))
    return algorithm.assign_ownership(mesh.array(0), mesh.array(3), rows, rules)


def baseline_source(model, i, value):
    identity = (i, "SCP" if i < 2 else "MUSCLE", str(i), "SOURCE")
    owners = (str(i),) if i < 2 else ("0", "1")
    return model.TopologyOwnershipSource(*identity, owners, value.array(0), value.array(3))


def compare(engine, mesh, inputs):
    capture = skin_capture.capture(
        engine, inputs, [np.eye(4).ravel()] * 3, [(1, 1, i < 2) for i in range(3)]
    )
    start = perf_counter()
    expected = baseline(mesh, inputs)
    addon_seconds = perf_counter() - start
    start = perf_counter()
    actual = skin_ownership.evaluate(mesh, capture, [0, 3, 6, 9], [0, 1, -1], [[0], [1], [0, 1]])
    seconds = perf_counter() - start
    np.testing.assert_array_equal(actual.owners, expected.owner_indices)
    return report(mesh, actual, addon_seconds, seconds)


def report(mesh, actual, addon_seconds, seconds):
    return dict(
        vertices=mesh.counts[0],
        mismatches=0,
        addon_seconds=addon_seconds,
        native_seconds=seconds,
        fallback_count=actual.fallback_count,
    )


def main():
    addon(Path(sys.argv[1]))
    engine = GeometryEngine()
    inputs = sources(engine)
    reports = [compare(engine, grid(engine, size)[0], inputs) for size in (20, 40, 100)]
    path = Path("build/skin-040/ownership-parity.json")
    path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
