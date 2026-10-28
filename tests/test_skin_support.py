"""Source selection, both-side sampling, retained identity and native assembly."""

import numpy as np
import pytest

from anthroforge.application import skin_support_capture as capture
from anthroforge.core import skin_sources
from anthroforge.core.entities import IDENTITY
from anthroforge.native import skin_deformation, skin_support, tissue_parts
from anthroforge.native.mesh import NativeCancellation
from tests.test_skin_capture import triangle
from tests.test_tissue_branches import CASES, inputs
from tests.test_tissue_envelopes import side
from tests.test_tissue_workflow import assembly


def test_sampling_matches_original_area_cdf_and_world_units(session):
    mesh = triangle(session.engine)
    frame = list(IDENTITY)
    frame[0] = -2
    ids, points, mass = skin_support.sample(mesh, frame)
    expected = mesh.array(0).copy()
    expected[:, 0] *= -2
    old_ids, old_mass = skin_deformation.sample_surface(session.engine, expected, [[0, 1, 2]])
    np.testing.assert_array_equal(ids, old_ids)
    np.testing.assert_array_equal(points, expected[ids])
    assert mass == old_mass == 1
    np.testing.assert_allclose(
        skin_support.weights(session.engine, [1, 3], [3, 2]), [1 / 12] * 3 + [3 / 8] * 2
    )


def test_both_inflated_sides_supply_samples(session):
    base, parts = inputs(session, CASES[0])
    first, second = side(base, parts, False, False), side(base, parts, True, False)
    mesh = tissue_parts.compose(first, second, False)
    ids, points, _ = skin_support.sample(mesh, IDENTITY)
    from anthroforge.native import tissue_domain

    records, _ = tissue_domain.arrays(mesh)
    assert len(ids) == 80 and records[1] == 5
    assert np.any(ids >= first.counts[0])
    np.testing.assert_allclose(skin_support.targets(mesh, mesh, IDENTITY, ids), points)


def test_missing_identity_and_cancellation_do_not_rebind(session):
    mesh = triangle(session.engine)
    bigger = session.engine.create_mesh(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], [0, 1, 2, 3], [0, 4]
    )
    with pytest.raises(ValueError, match="topology changed"):
        skin_support.targets(mesh, bigger, IDENTITY, [0])
    with pytest.raises(ValueError, match="identity"):
        skin_support.targets(mesh, mesh, IDENTITY, [9])
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_support.sample(mesh, IDENTITY, token.handle)


def test_surface_choice_uses_accepted_stage_and_captures_policy(session):
    _, _, tissue = assembly(session)
    item = session.document.object(tissue)
    identity = skin_sources.Source(tissue, "TISSUE")
    args = session.engine, session.document, session.resources
    assert capture.source(*args, identity, "FINISHED").asset == item.final_result.asset
    assert capture.source(*args, identity, "INFLATED_REST").asset == item.rest_material.rest
    for policy in ("FINISHED", "INFLATED_REST"):
        value = capture.capture(*args, policy)
        np.testing.assert_allclose(capture.targets(*args, value.data), value.data.arrays["samples"])
        assert value.sources


def test_skin_preference_persists_without_edit_or_job(session):
    before, history = session.document, tuple(session.history.entries)
    assert session.command("preferences.get")["skin_tissue_surface"] == "FINISHED"
    session.command("preferences.set", skin_tissue_surface="INFLATED_REST")
    assert session.document is before and tuple(session.history.entries) == history
    assert not session.scheduler.blocked
    with pytest.raises(ValueError, match="Skin tissue surface"):
        session.command("preferences.set", skin_tissue_surface="BASE")
