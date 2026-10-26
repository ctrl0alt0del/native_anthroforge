"""Transitions preserve addon policies, parity restrictions and immutable boundaries."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_stitch
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_stitch import evaluate

DATA = json.loads((Path(__file__).parent / "fixtures/skin/stitch.json").read_text())
MODES = ("SPARSE", "STAGED", "CENTERED")


def compare_diagnostics(actual, expected):
    assert MODES[int(actual[0])] == expected["mode"]
    fields = (
        "selected_seam_shift",
        "candidate_count",
        "local_intersections",
        "boundary_count",
        "annulus_count",
        "aspect_p95",
        "aspect_max",
    )
    np.testing.assert_allclose(actual[2:], [expected[name] for name in fields], atol=2e-12)


@pytest.mark.parametrize("row", DATA["cases"])
def test_transition_matches_addon_or_rejects_same_unsupported_pair(session, row):
    if "error" in row:
        with pytest.raises(ValueError, match="parity|symmetry|symmetric|boundary"):
            evaluate(session.engine, row)
        return
    result = evaluate(session.engine, row)
    np.testing.assert_allclose(result.topology.mesh.array(0), row["points"], atol=1e-12)
    np.testing.assert_array_equal(result.topology.mesh.array(1).reshape(-1, 4), row["faces"])
    compare_diagnostics(result.diagnostics, row["diagnostics"])
    assert np.all(result.topology.regions == 1) and np.all(result.topology.guides == -1)


def test_transition_rejects_cancelled_and_malformed_inputs(session):
    row = DATA["cases"][0]
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_stitch.build(session.engine, row["first"], row["second"], 8, cancel=token.handle)
    with pytest.raises(ValueError, match="finite nonzero"):
        skin_stitch.build(session.engine, np.zeros((4, 3)), row["second"], 8)
    with pytest.raises(ValueError, match="positive diagonal"):
        skin_stitch.build(session.engine, row["first"], row["second"], np.nan)
