"""Advisory validation agrees with the production addon and reports missing checks."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_topology, skin_validation
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_assembly import quads

DATA = json.loads((Path(__file__).parent / "fixtures/skin/quality.json").read_text())
FIELDS = (
    "finite",
    "all_quads",
    "components",
    "orientable",
    "manifold",
    "no_degenerates",
    "max_valence",
    "valence_ok",
    "degenerate_faces",
)


@pytest.mark.parametrize("row", DATA["cases"], ids=lambda row: row["name"])
def test_advisory_topology_matches_addon(session, row):
    mesh = quads(session.engine, row["vertices"], row["faces"])
    result = skin_topology.Result(mesh, np.zeros(mesh.counts[1]), None)
    envelope = session.engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)
    actual = skin_validation.evaluate(result, envelope, 0, 0)
    assert {key: actual[key] for key in FIELDS} == {key: row["expected"][key] for key in FIELDS}
    assert actual["self_intersections"] is None
    np.testing.assert_array_equal(mesh.array(0), row["vertices"])


def test_quality_distance_units_and_symmetry_cancellation(session):
    points = [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]]
    envelope = quads(session.engine, points, [[0, 1, 2, 3]])
    moved = quads(session.engine, np.array(points) + [0, 0, 0.1], [[0, 1, 2, 3]])
    result = skin_topology.Result(moved, np.array([2]), None)
    report = skin_validation.evaluate(result, envelope, 1, 1, [0, 0, 0, 1, 0, 0])
    assert report["fidelity_p95"] == pytest.approx(0.1) and report["fidelity_ok"] == 0
    assert report["guide_preserved"] and report["symmetry_ok"] and report["boundary_match"]
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_validation.evaluate(result, envelope, 1, 1, cancel=token.handle)
