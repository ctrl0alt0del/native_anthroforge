"""Exact source contact behavior remains advisory, including incomplete CCD coverage."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_contact
from anthroforge.native.mesh import NativeCancellation

FIXTURE = json.loads((Path(__file__).parent / "fixtures/skin/contact.json").read_text())


@pytest.mark.parametrize("name", ["identity", "crossing", "reopening"])
def test_source_contact_projection_and_diagnostics(session, name):
    case = FIXTURE["cases"][name]
    points, report = skin_contact.evaluate(
        session.engine, FIXTURE, case["current"], case["proposed"], 1 << 30
    )
    np.testing.assert_allclose(points, case["result"]["points"], atol=1e-10)
    np.testing.assert_allclose(report, case["result"]["diagnostics"], atol=1e-10)
    assert report[6] == 1  # Source reports incomplete collision coverage, never full safety.


def test_source_symmetry_and_disabled_symmetry(session):
    ids, error = skin_contact.symmetry(
        session.engine, FIXTURE["vertices"], FIXTURE["symmetry_plane"]
    )
    np.testing.assert_array_equal(ids, FIXTURE["symmetry_partners"])
    assert error == pytest.approx(FIXTURE["symmetry_error"])
    disabled, _ = skin_contact.symmetry(session.engine, FIXTURE["vertices"], None)
    assert np.all(disabled == -1)


def test_contact_cancellation_and_original_storage_limit(session):
    cancel = NativeCancellation(session.engine)
    cancel.set()
    points = FIXTURE["vertices"]
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_contact.evaluate(session.engine, FIXTURE, points, points, 1 << 30, cancel.handle)
    with pytest.raises(ValueError, match="CONTACT_MEMORY_LIMIT"):
        skin_contact.evaluate(session.engine, FIXTURE, points, points, 1)
