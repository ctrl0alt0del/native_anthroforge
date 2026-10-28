"""Reuse only fixed-reference preparation; cache admission never rejects a valid solve."""

import numpy as np
import pytest

from anthroforge.native import skin_deformation
from tests.test_skin_reference import build, topology


@pytest.mark.parametrize("mode", ["LE", "FAST"])
def test_reference_preparation_reused_and_independent_of_target_pose(session, mode):
    topology(session)
    session.command("skin.configure", section="deformation_settings", values={"method": mode})
    skin = build(session)
    ref = session.resources.skin[skin.reference]
    settings = skin.deformation_settings
    cached = skin_deformation.cached(session.engine, ref.digest, ref.arrays, settings)
    assert cached is session.engine.skin_preparations.get((ref.digest, settings))
    targets = ref.arrays["samples"] + (0, 0.02, 0)
    actual, _, _ = cached.solve(targets)
    with skin_deformation.Preparation(session.engine, ref.arrays, settings) as fresh:
        expected, _, _ = fresh.solve(targets)
    np.testing.assert_array_equal(actual, expected)
    assert cached.bytes > ref.arrays["proxy_vertices"].nbytes


def test_cache_budget_bypass_does_not_restrict_computation(session):
    session.engine.skin_preparations.budget = 1
    topology(session)
    skin = build(session)
    ref = session.resources.skin[skin.reference]
    assert not session.engine.skin_preparations.items
    prepared = skin_deformation.cached(
        session.engine, ref.digest, ref.arrays, skin.deformation_settings
    )
    result, _, _ = prepared.solve(ref.arrays["samples"])
    np.testing.assert_allclose(result, ref.arrays["vertices"], atol=1e-8)
    assert not session.engine.skin_preparations.items
