"""Achieved budgets vote by owner before grouping into exclusive subtrees."""

import numpy as np
import pytest

from anthroforge.application.skin_density import budget_warnings
from anthroforge.native import skin_density, skin_ownership
from anthroforge.native.mesh import NativeCancellation
from tests.test_skin_final_diagnostics import DATA
from tools.check_skin_assembly import quads


def mesh(session):
    points = [
        [x, y, 0]
        for i in range(4)
        for x, y in ((3 * i, 0), (3 * i + 1, 0), (3 * i + 1, 1), (3 * i, 1))
    ]
    return quads(session.engine, points, DATA["budgets"]["faces"])


def test_budget_majority_ties_and_missing_owners_match_addon(session):
    source = mesh(session)
    ids = DATA["budgets"]["owners"]
    owners, _ = skin_ownership.sample(source, source, ids, np.ones(16))
    # All owners 0/1 share one subtree, but must not merge their votes before majority.
    actual = skin_density.achieved(source, owners, [0, 0, 1], 3)
    expected = np.bincount(
        [0 if i in (0, 1) else 1 if i == 2 else 2 for i in DATA["budgets"]["expected"]]
    )
    np.testing.assert_array_equal(actual, expected)
    assert actual.sum() == 4


def test_budget_warning_uses_addon_strict_twenty_percent_threshold():
    row = dict(owner="root", exclusive=100, actual_exclusive_quads=120)
    assert not budget_warnings([row])
    assert budget_warnings([dict(row, actual_exclusive_quads=121)])
    assert not budget_warnings([dict(row, exclusive=0)])


def test_invalid_and_cancelled_budget_counts_fail(session):
    source = mesh(session)
    with pytest.raises(ValueError, match="owner"):
        skin_density.achieved(source, np.full(16, 3), [0], 2)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_density.achieved(source, np.zeros(16), [0], 2, token.handle)
