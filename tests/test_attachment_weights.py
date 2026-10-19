"""Exact addon owner transitions, hard constraints and native cancellation."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import attachment_weights
from anthroforge.native.mesh import NativeCancellation

CASES = json.loads(Path("tests/fixtures/attachments/owner_weights.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_native_owner_weights_match_addon_reference(session, case):
    targets, weights = attachment_weights.owners(
        session.engine, case["points"], case["owners"], case["pins"], case["closed"]
    )
    for index, reference in enumerate(case["influences"]):
        assert targets[index, : len(reference)].tolist() == [row[0] for row in reference]
        np.testing.assert_allclose(
            weights[index, : len(reference)], [r[1] for r in reference], atol=1e-13
        )
        assert np.all(targets[index, len(reference) :] == -1)
        assert np.all(weights[index, len(reference) :] == 0)
    np.testing.assert_allclose(weights.sum(axis=1), 1)


def test_owner_blending_rejects_missing_pins_and_honors_cancellation(session):
    args = (session.engine, [[0, 0, 0], [1, 0, 0], [2, 0, 0]], [0, 1, 1])
    with pytest.raises(ValueError, match="endpoints"):
        attachment_weights.owners(*args, [1], False)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        attachment_weights.owners(*args, [0, 2], False, cancel.handle)
