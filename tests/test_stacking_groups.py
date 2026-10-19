"""Native grouped sides retain receiving settings, parity and cancellation ownership."""

from copy import deepcopy

import numpy as np
import pytest

from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.stacking import resolve_group, results
from tests.test_stacking_phases import planned
from tests.test_tissue_stacking_native import CASES, assert_same_output


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_single_session_group_matches_qualified_pipeline(session, case):
    native, initial, _ = planned(session, case)
    output = resolve_group(session.engine, {key: native for key in initial}, {})
    for key, expected in case["output"].items():
        row = output[int(key)]
        assert row["status"] == expected["status"], row["message"]
        assert row["message"] == expected["message"]
        np.testing.assert_allclose(row["points"], expected["points"], atol=2e-7, rtol=0)


def test_each_receiver_uses_its_own_settings_and_cancel_restores_all_sessions(session):
    changed = deepcopy(CASES[0])
    changed["settings"]["stacking"]["clearance"] = 0.02
    first, initial, orders = planned(session, CASES[0])
    second, _, _ = planned(session, changed)
    expected, _ = second.resolve({}, tuple(initial))
    receiver = next(row.covering for row in orders if row.status == 0)
    owners = {key: second if key == receiver else first for key in initial}
    output = resolve_group(session.engine, owners, {})
    assert_same_output(expected, output)
    check_cancel(session, owners)


def check_cancel(session, owners):
    before = {native: results(native)[0] for native in owners.values()}
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="CANCELLED"):
        resolve_group(session.engine, owners, {}, cancel.handle)
    for native, output in before.items():
        assert_same_output(output, results(native)[0])
