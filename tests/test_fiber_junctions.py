"""Shared points retain one binding choice across edits, evaluation and history."""

import numpy as np
import pytest

from tests.test_fiber_creation import bind, path, scene
from tests.test_fiber_editing import edited_point, second_surface
from tests.test_junction_workflow import reference


def connected(session):
    target, source = scene(session)
    other = second_surface(session, target)
    a, b = bind(session, target, source), bind(session, other, source)
    junction = session.command(
        "junction.create", source=reference(session, a.id), targets=[reference(session, b.id)]
    )
    session.wait()
    assert_ready(session, a.id, b.id)
    return target, other, a.id, b.id, junction


def assert_ready(session, *keys):
    for key in keys:
        item = session.document.object(key)
        assert item.result.status == "ready", item.result.error
        assert getattr(item, "edit", None) is None
    np.testing.assert_allclose(
        path(session, keys[0])[0, :3], path(session, keys[1])[0, :3], atol=1e-12
    )


def bindings(session, a, b):
    left, right = (session.document.object(key).bindings[0] for key in (a, b))
    assert left.target == right.target and left.attachment == right.attachment
    assert left.capture_scope == right.capture_scope
    return left


def test_join_adopts_the_source_binding_and_parent_motion_retains_it(session):
    target, other, a, b, _ = connected(session)
    before = bindings(session, a, b)
    assert before.target == target
    for z in (1, 0, 2, 0):
        session.command("scp.transform", entity=other, values=[3, 0, z, 0, 0, 0, 1, 1, 1])
        session.wait()
        assert_ready(session, a, b)
        assert bindings(session, a, b) == before


def test_follower_edit_rebinds_through_source_and_undo_is_atomic(session):
    target, _, a, b, _ = connected(session)
    before = bindings(session, a, b)
    count = session.history.cursor
    edited_point(session, b, 0, [-0.2, 0.1, 0.8])
    assert_ready(session, a, b)
    assert bindings(session, a, b) != before
    assert session.history.cursor == count + 1
    session.command("undo")
    session.wait()
    assert_ready(session, a, b)
    assert bindings(session, a, b) == before


def test_any_parent_choice_is_shared_after_source_publication(session):
    _, other, a, b, _ = connected(session)
    session.command("fiber.binding.scope", **reference(session, b), scope="ANY_PARENT")
    session.wait()
    assert bindings(session, a, b).capture_scope == "ANY_PARENT"
    edited_point(session, b, 0, [3, 0.1, 0.7])
    assert_ready(session, a, b)
    assert bindings(session, a, b).target == other


def test_explicit_binding_assignment_on_follower_updates_all_members(session):
    _, other, a, b, _ = connected(session)
    session.command("fiber.binding.set", **reference(session, b), target=other)
    session.wait()
    assert_ready(session, a, b)
    assert bindings(session, a, b).target == other


def test_unbound_curve_cannot_own_a_mandatory_fiber_binding(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before = session.document
    with pytest.raises(ValueError, match="bound fiber point"):
        session.command(
            "junction.create",
            source=reference(session, source),
            targets=[reference(session, fiber.id)],
        )
    assert session.document == before


def test_bound_fiber_can_drive_ordinary_curve_and_roundtrip(session, tmp_path):
    target, source = scene(session)
    fiber = bind(session, target, source)
    session.command(
        "junction.create", source=reference(session, fiber.id), targets=[reference(session, source)]
    )
    session.wait()
    location = tmp_path / "junction.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    assert_ready(session, fiber.id, source)


def test_manual_source_keeps_accepted_binding_until_explicit_evaluation(session):
    _, other, a, b, _ = connected(session)
    before = bindings(session, a, b)
    session.command("update_mode", entity=a, mode="MANUAL")
    session.command("fiber.binding.set", **reference(session, a), target=other)
    session.wait()
    follower = session.document.object(b)
    assert follower.bindings[0].target == before.target and a in follower.result.pending
    session.command("curve.evaluate", curve=a)
    session.wait()
    assert_ready(session, a, b)
    assert bindings(session, a, b).target == other


def test_source_parent_motion_does_not_recapture_or_accumulate_drift(session):
    target, _, a, b, _ = connected(session)
    original = {key: path(session, key) for key in (a, b)}
    binding = bindings(session, a, b)
    for z in (1, 0, 2, 0):
        session.command("scp.transform", entity=target, values=[0, 0, z, 0, 0, 0, 1, 1, 1])
        session.wait()
        assert_ready(session, a, b)
        assert bindings(session, a, b) == binding
    for key in (a, b):
        np.testing.assert_allclose(path(session, key), original[key], atol=1e-12)
