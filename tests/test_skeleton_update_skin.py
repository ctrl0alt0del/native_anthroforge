"""Optional skin preview deforms existing topology and never regenerates construction."""

import numpy as np

from tests.test_skeleton_update_commands import prepare, replacement
from tests.test_skeleton_update_controls import apply
from tests.test_skeleton_update_placements import different_topology
from tests.test_skin_reference import build, topology


def test_skin_preview_is_position_only_and_apply_adopts_it(session, tmp_path):
    bone = topology(session)
    skin = build(session)
    before = session.assets[skin.final.asset].mesh
    path = replacement(session, bone, tmp_path, offset=[0, 0, 0.1])
    state = prepare(session, path, {bone: bone}, preview_skin=True)
    assert state["skin"]["previewed"], state
    candidate = session.skeleton_update.ready(state["token"])
    changed = candidate.resources.meshes[candidate.document.skin.final.asset].mesh
    np.testing.assert_array_equal(changed.array(1), before.array(1))
    np.testing.assert_array_equal(changed.array(2), before.array(2))
    np.testing.assert_allclose(changed.array(0), before.array(0) + [0, 0, 0.1], atol=1e-6)
    apply(session, state)
    assert session.document.skin.topology == skin.topology
    assert session.document.skin.final == candidate.document.skin.final


def test_changed_topology_invalidates_skin_without_regenerating_it(session, tmp_path):
    bone = topology(session)
    before = build(session)
    state = prepare(
        session, different_topology(session, bone, tmp_path), {bone: bone}, preview_skin=True
    )
    assert not state["skin"]["available"] and not state["skin"]["previewed"]
    apply(session, state)
    assert session.document.skin.topology == before.topology
    assert session.document.skin.final.asset == before.final.asset
    assert session.document.skin.final.status == "invalid"
