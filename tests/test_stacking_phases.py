"""Candidate planning and frozen-provider solves preserve the qualified numerical path."""

import numpy as np
import pytest

from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.stacking import StackSession, results
from tests.stacking_fixtures import domain, options, settings
from tests.test_tissue_stacking_native import CASES, assert_same_output


def planned(session, case):
    packed = [domain(row) for row in case["domains"]]
    native = StackSession(session.engine)
    arguments, _leases = options(case)
    output, orders = native.plan([r[0] for r in packed], settings(case["settings"]), **arguments)
    return native, output, orders


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_separated_plan_and_solve_match_production(session, case):
    native, initial, _ = planned(session, case)
    for record in case["domains"]:
        np.testing.assert_array_equal(initial[record["id"]]["points"], record["own"])
    output, _ = native.resolve({}, tuple(initial))
    for key, expected in case["output"].items():
        row = output[int(key)]
        assert row["status"] == expected["status"], row["message"]
        assert row["message"] == expected["message"]
        np.testing.assert_allclose(row["points"], expected["points"], atol=2e-7, rtol=0)


def test_frozen_provider_matches_full_solve(session):
    case = CASES[0]
    native, initial, orders = planned(session, case)
    full, _ = native.resolve({}, tuple(initial))
    target = next(row.covering for row in orders if row.status == 0)
    providers = {key: row for key, row in full.items() if key != target}
    resolved, _ = native.resolve(providers, (target,))
    assert_same_output(full, resolved)


def test_missing_provider_fails_without_recomputing_it(session):
    native, _, orders = planned(session, CASES[0])
    target = next(row.covering for row in orders if row.status == 0)
    output, _ = native.resolve({}, (target,))
    assert output[target]["status"] == 2
    assert "ACCEPTED_PREREQUISITE_UNAVAILABLE" in output[target]["message"]


def test_failed_provider_does_not_publish_current_intrinsic_as_final(session):
    native, initial, orders = planned(session, CASES[0])
    target = next(row.covering for row in orders if row.status == 0)
    frozen = {key: dict(row, status=2) for key, row in initial.items() if key != target}
    output, _ = native.resolve(frozen, (target,))
    assert output[target]["status"] == 2
    assert "BLOCKED_BY_PROVIDER" in output[target]["message"]


def test_cancelled_resolve_retains_previous_output(session):
    native, initial, _ = planned(session, CASES[0])
    before, _ = native.resolve({}, tuple(initial))
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="CANCELLED"):
        native.resolve({}, tuple(initial), cancel.handle)
    assert_same_output(before, results(native)[0])


def test_frozen_provider_is_not_overwritten_by_neighbor_failure(session):
    native, initial, orders = planned(session, CASES[0])
    target = next(row.covering for row in orders if row.status == 0)
    frozen = {
        key: dict(row, points=row["points"] + [0, 0, 20])
        for key, row in initial.items()
        if key != target
    }
    output, _ = native.resolve(frozen, (target,))
    assert_same_output(frozen, output)
