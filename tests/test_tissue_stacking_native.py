"""Production vector pipeline parity, exact equations, rejections and synchronous lifecycle."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.stacking import StackSession, results
from tests.stacking_fixtures import domain, options, settings

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/stacking.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_vector_pipeline_matches_production_addon(session, case):
    packed = [domain(row) for row in case["domains"]]
    native = StackSession(session.engine)
    arguments, _leases = options(case)
    result, _ = native.run([r[0] for r in packed], settings(case["settings"]), **arguments)
    for key, expected in case["output"].items():
        row = result[int(key)]
        assert row["status"] == expected["status"], row["message"]
        assert row["message"] == expected["message"]
        np.testing.assert_allclose(row["points"], expected["points"], atol=2e-7, rtol=0)


def test_repeated_solve_reuses_cache_and_preserves_last_result_on_cancel(session):
    case = CASES[0]
    packed = [domain(row) for row in case["domains"]]
    native, options = StackSession(session.engine), settings(case["settings"])
    native.run([r[0] for r in packed], options)
    output, _ = native.run([r[0] for r in packed], options)
    assert any(row["metrics"][23] for row in output.values())
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancelled|CANCELLED"):
        native.run([r[0] for r in packed], options, cancel=cancel.handle)
    assert_same_output(output, results(native)[0])


def assert_same_output(before, after):
    for key in before:
        np.testing.assert_array_equal(before[key]["points"], after[key]["points"])
