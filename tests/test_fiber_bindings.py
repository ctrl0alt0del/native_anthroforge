"""Binding lifecycle, topology edits and resolved-shape authoring share one transaction path."""

import numpy as np
import pytest

from anthroforge.application.curve_edit_state import current
from anthroforge.application.workspace_policy import included
from anthroforge.core.entities import Workspace
from tests.test_fiber_creation import bind, path, scene
from tests.test_fiber_editing import moved_fiber, second_surface


def assign(session, fiber, point, target):
    session.command("fiber.binding.set", curve=fiber, point=point, target=target)
    session.wait()
    item = session.document.object(fiber)
    assert item.result.status == "ready", item.result.error
    assert item.edit is None and all(b.attachment for b in item.bindings)
    return item


def test_structural_binding_add_remove_preserves_shape_and_undo(session):
    target, key = moved_fiber(session)
    before, shape = session.document.object(key), path(session, key)
    point = before.points[1].id
    cursor = session.history.cursor
    item = assign(session, key, point, target)
    assert len(item.bindings) == 3 and session.history.cursor == cursor + 1
    np.testing.assert_allclose(path(session, key), shape, atol=1e-12)
    session.command("fiber.binding.remove", curve=key, point=point)
    session.wait()
    assert len(session.document.object(key).bindings) == 2
    session.navigate(-1)
    assert session.document.object(key).bindings == item.bindings


def test_reassignment_keeps_current_shape_then_follows_chosen_parent(session):
    target, source = scene(session)
    other = second_surface(session, target)
    fiber = bind(session, target, source)
    shape = path(session, fiber.id)
    item = assign(session, fiber.id, fiber.points[0].id, other)
    assert item.bindings[0].target == other
    np.testing.assert_allclose(path(session, fiber.id), shape, atol=1e-12)
    session.command("scp.transform", entity=other, values=[3, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(path(session, fiber.id)[0, :3], shape[0, :3] + [0, 0, 1])
    np.testing.assert_allclose(path(session, fiber.id)[-1, :3], shape[-1, :3], atol=1e-12)


def test_mandatory_binding_removal_rejected_without_a_partial_edit(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before = session.document
    with pytest.raises(ValueError, match="both endpoint"):
        session.command("fiber.binding.remove", curve=fiber.id, point=fiber.points[0].id)
    assert session.document == before


def test_endpoint_extension_and_deletion_transfer_mandatory_binding(session):
    target, key = moved_fiber(session)
    old = session.document.object(key)
    added = session.command(
        "curve.point.insert", curve=key, index=0, point=dict(position=[-0.7, 0.1, 1.7])
    )
    session.wait()
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    assert item.bindings[0].point == added
    assert item.bindings[0].target == old.bindings[0].target
    session.command("curve.point.remove", curve=key, point=added)
    session.wait()
    assert session.document.object(key).bindings == old.bindings


def test_closed_fiber_opening_requires_endpoint_choices(session):
    target, source = scene(session, closed=True)
    fiber = bind(session, target, source)
    with pytest.raises(ValueError, match="both endpoint"):
        session.command("curve.edit", curve=fiber.id, closed=False)
    assign(session, fiber.id, fiber.points[-1].id, target)
    session.command("curve.edit", curve=fiber.id, closed=False)
    session.wait()
    item = session.document.object(fiber.id)
    assert not item.closed and item.result.status == "ready", item.result.error


def test_noop_edit_of_current_shape_does_not_create_history_or_job(session):
    target, key = moved_fiber(session)
    item = current(session, session.document.object(key))
    cursor, jobs, before = session.history.cursor, len(session.scheduler.jobs), session.document
    session.command(
        "curve.point.update", curve=key, point=item.points[1].id, position=item.points[1].position
    )
    assert session.document is before
    assert session.history.cursor == cursor and len(session.scheduler.jobs) == jobs


def pending_project(session, location):
    target, source = scene(session)
    fiber = bind(session, target, source)
    session.command("update_mode", entity=fiber.id, mode="MANUAL")
    point = fiber.points[1].id
    session.command("fiber.binding.set", curve=fiber.id, point=point, target=target)
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    return fiber, point


def test_pending_binding_roundtrip_retains_request_until_manual_evaluation(session, tmp_path):
    location = tmp_path / "pending.anthroforge"
    fiber, point = pending_project(session, location)
    session.command("open", path=str(location))
    session.wait()
    item = session.document.object(fiber.id)
    assert item.edit and any(b.point == point and b.attachment is None for b in item.bindings)
    session.command("curve.evaluate", curve=fiber.id)
    session.wait()
    assert session.document.object(fiber.id).edit is None


def test_fiber_is_associated_with_its_chosen_anatomical_parents(session):
    target, source = scene(session)
    other = second_surface(session, target)
    fiber = bind(session, target, source)
    focus = Workspace(name="Other surface", focused=True, members=(other,))
    assert not included(session.document, focus, fiber.id)
    assign(session, fiber.id, fiber.points[0].id, other)
    assert included(session.document, focus, fiber.id)


def test_consumer_endpoint_edit_uses_same_binding_policy(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    body = session.command("primitive.from_curves", curves=[fiber.id], kind="BODY", parent=target)
    session.wait()
    session.command("point.remove", entity=body, curve=fiber.id, point=fiber.points[0].id)
    session.wait()
    item = session.document.object(fiber.id)
    assert item.result.status == "ready", item.result.error
    assert item.bindings[0].point == fiber.points[1].id
    assert item.bindings[0].target == target
    assert session.document.entity(body).result.status == "ready"
