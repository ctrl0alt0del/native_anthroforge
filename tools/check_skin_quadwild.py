"""Compare the maintained addon pipeline and standalone adapter on the same compact input."""

import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np

from anthroforge.application import quadwild_backend, quadwild_bundle
from anthroforge.application.quadwild_steps import Execution
from anthroforge.native.mesh import GeometryEngine, NativeCancellation
from anthroforge.native.skin_guides import Guides


def addon(root):
    for suffix in ("", ".core", ".core.topology"):
        name = "addon_reference" + suffix
        package = types.ModuleType(name)
        package.__path__ = [str(root.joinpath(*suffix.strip(".").split(".")))]
        sys.modules[name] = package
    return importlib.import_module("addon_reference.core.topology.quadwild")


def inputs(engine, folder):
    mesh = engine.import_mesh(Path("examples/primitives/cube.obj").resolve(), 1, False)
    guides = Guides(np.empty((0, 10)), np.empty((0, 3)), np.array([0]))
    path = folder / "input.npz"
    np.savez(
        path,
        vertices=mesh.array(0),
        faces=mesh.array(3),
        flow_samples=guides.samples,
        flow_points=guides.points,
        flow_offsets=guides.offsets,
    )
    return mesh, guides, path


def compare(actual, expected):
    np.testing.assert_allclose(actual.array(0), expected["vertices"], atol=1e-12, rtol=0)
    np.testing.assert_array_equal(actual.array(1).reshape(-1, 4), expected["faces"])
    return dict(
        vertices=actual.counts[0],
        quads=actual.counts[1],
        maximum_error=float(np.max(np.abs(actual.array(0) - expected["vertices"]))),
    )


def main():
    root, destination = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
    source, target = destination / "addon", destination / "standalone"
    source.mkdir(parents=True)
    target.mkdir(parents=True)
    engine = GeometryEngine()
    mesh, guides, path = inputs(engine, source)
    addon(root).run(path, source / "output.npz", 64)
    context = Execution(engine, quadwild_bundle.verify(), NativeCancellation(engine))
    actual = quadwild_backend.run(context, mesh, guides, 64, target)
    with np.load(source / "output.npz", allow_pickle=False) as expected:
        evidence = compare(actual.mesh, expected) | dict(warnings=actual.warnings)
    (destination / "parity.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
