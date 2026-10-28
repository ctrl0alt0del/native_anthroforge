"""Direct maintained-addon numerical parity, cancellation and owned solver lifetime."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_deformation as native
from anthroforge.native.mesh import NativeCancellation

FIXTURE = json.loads((Path(__file__).parent / "fixtures/skin/deformation.json").read_text())


@pytest.mark.parametrize("method", ["LE", "FAST"])
def test_addon_solver_parity_and_retained_embedding(session, method):
    settings = replace(DeformationSettings(), method=method, fast_handles=5)
    expected = FIXTURE["results"][method]
    with native.Preparation(session.engine, FIXTURE["arrays"], settings) as solver:
        ids, weights = solver.embedding()
        np.testing.assert_array_equal(ids, expected["embedding_indices"])
        np.testing.assert_allclose(weights, expected["embedding_weights"], atol=1e-12)
        for name, targets in FIXTURE["targets"].items():
            compare(solver.solve(targets), expected["cases"][name])
        assert solver.bytes > 0
    assert solver.handle == 0


def compare(result, expected):
    points, report, predicted = result
    np.testing.assert_allclose(points, expected["points"], atol=1e-9, rtol=1e-9)
    np.testing.assert_allclose(predicted, expected["predicted"], atol=1e-9, rtol=1e-9)
    np.testing.assert_allclose(report, expected["diagnostics"], atol=1e-8, rtol=1e-8)


def test_addon_area_cdf_sampling(session):
    data = FIXTURE["sampling"]
    ids, mass = native.sample_surface(session.engine, data["points"], data["faces"])
    np.testing.assert_array_equal(ids, data["selected"])
    assert mass == pytest.approx(data["mass"], abs=1e-12)


def test_cancelled_solve_does_not_poison_preparation(session):
    cancel = NativeCancellation(session.engine)
    with native.Preparation(session.engine, FIXTURE["arrays"], DeformationSettings()) as solver:
        cancel.set()
        with pytest.raises(ValueError, match="[Cc]ancel"):
            solver.solve(FIXTURE["targets"]["identity"], cancel.handle)
        points, _, _ = solver.solve(FIXTURE["targets"]["identity"])
        np.testing.assert_allclose(points, FIXTURE["arrays"]["vertices"], atol=1e-12)


def test_invalid_samples_and_released_handles_fail(session):
    with native.Preparation(session.engine, FIXTURE["arrays"], DeformationSettings()) as solver:
        with pytest.raises(ValueError, match="match retained"):
            solver.solve([[0, 0, 0]])
        targets = np.array(FIXTURE["targets"]["identity"])
        targets[0, 0] = np.nan
        with pytest.raises(ValueError, match="finite"):
            solver.solve(targets)
    with pytest.raises(ValueError, match="expired"):
        solver.solve(FIXTURE["targets"]["identity"])
