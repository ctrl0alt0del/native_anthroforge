"""Final-skin findings preserve addon predicates and remain advisory publications."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application import skin_assets
from anthroforge.application import skin_final_diagnostics as report
from anthroforge.application.issues import skin as issues
from anthroforge.native import skin_final_quality as native
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_assembly import quads

DATA = json.loads((Path(__file__).parent / "fixtures/skin/final_quality.json").read_text())


@pytest.mark.parametrize("row", DATA["cases"], ids=lambda row: row["name"])
def test_final_intersections_match_actual_addon(session, row):
    mesh = quads(session.engine, row["vertices"], row["faces"])
    assert native.intersections(mesh, 64 * 1024**2) == row["intersections"]
    np.testing.assert_array_equal(mesh.array(0), row["vertices"])


@pytest.mark.parametrize("row", DATA["cases"], ids=lambda row: row["name"])
def test_sampled_clearance_matches_actual_addon(session, row):
    mesh = quads(session.engine, row["vertices"], row["faces"])
    moved = quads(session.engine, np.array(row["vertices"]) * [1, 1, 1.2], row["faces"])
    samples = np.array(row["samples"])
    actual = native.clearance(mesh, moved, samples, samples + [0, 0.2, 0])
    for name, value in row["clearance"]["anatomy_clearance"].items():
        if name != "interpretation":
            assert actual[name] == pytest.approx(value, abs=1e-12)


def test_solver_and_contact_findings_are_visible_in_issues():
    ref = skin_assets.create({}, dict(settings=dict(method="FAST"), tissue_surface="FINISHED"))
    metadata = report.metadata(
        ref, [80, 0.1, -0.2, 10, 0.3, 0], [0, 100, 1, 0, -0.2, 7, 1, 0.03], {}
    )
    messages = " ".join(text for _, text in issues.computed_messages(metadata))
    expected = "inverted", "iteration limit", "extrapolates 10", "contact violations", "incomplete"
    for text in expected:
        assert text in messages
    assert metadata["contact"]["symmetry_error"] == 0.03
    assert metadata["solver"]["residual"] == 0.1


def test_intersection_witness_limit_does_not_claim_full_comparison():
    before = dict(self_intersections=300, intersection_witnesses=[[0, 1], [2, 3]])
    after = dict(self_intersections=2, intersection_witnesses=[[0, 1], [4, 5]])
    assert report.compare(before, after) == dict(
        inherited_witnesses=1, new_witnesses=1, complete=False
    )
    before["self_intersections"] = 2
    assert report.compare(before, after)["complete"]
    assert not report.compare(dict(incomplete="unavailable"), after)["complete"]


def test_advisory_failure_and_cancellation_are_distinct(session):
    row = DATA["cases"][0]
    mesh = quads(session.engine, row["vertices"], row["faces"])
    value = report.checked(lambda: native.intersections(mesh, 1))
    assert "memory limit" in value["incomplete"]
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        report.checked(lambda: native.intersections(mesh, 1024**2, token.handle))


def test_geometry_warning_does_not_hide_reference_limit():
    metadata = dict(intersections=dict(self_intersections=5), anatomy_clearance={})
    messages = " ".join(report.geometry_warnings(metadata))
    assert "5 self-intersections" in messages and "not fully validated" in messages
