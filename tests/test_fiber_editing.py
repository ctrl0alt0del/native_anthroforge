"""Current-shape edits retain dense deformation, canonical anchors and one-action history."""

import numpy as np

from anthroforge.application.curve_edit_state import current
from tests.test_fiber_creation import CUBE, bind, path, scene


def moved_fiber(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    return target, fiber.id


def edited_point(session, fiber, index, position):
    item = session.document.object(fiber)
    session.command(
        "curve.point.update", curve=fiber, point=item.points[index].id, position=position
    )
    session.wait()
    changed = session.document.object(fiber)
    assert changed.result.status == "ready", changed.result.error
    assert changed.edit is None
    return changed


def test_resolved_edit_query_does_not_author_or_resample(session):
    target, fiber = moved_fiber(session)
    before = session.document
    item = current(session, before.object(fiber))
    assert item.points[0].position[2] > 1
    for _ in range(3):
        assert current(session, before.object(fiber)).points == item.points
    assert session.document is before


def test_interior_edit_preserves_unchanged_anchor_records_and_one_undo(session):
    target, fiber = moved_fiber(session)
    before, shape = session.document.object(fiber), path(session, fiber)
    cursor = session.history.cursor
    changed = edited_point(session, fiber, 1, [0, 0.45, 1.8])
    assert changed.bindings == before.bindings
    np.testing.assert_allclose(path(session, fiber)[[0, -1], :3], shape[[0, -1], :3], atol=1e-12)
    np.testing.assert_allclose(changed.points[1].position, [0, 0.45, 1.8], atol=1e-12)
    assert session.history.cursor == cursor + 1
    session.navigate(-1)
    np.testing.assert_array_equal(path(session, fiber), shape)
    session.navigate(1)
    session.wait()
    assert session.document.object(fiber).attachment_asset == changed.attachment_asset


def test_parent_movement_after_edit_uses_retained_new_bindings(session):
    target, fiber = moved_fiber(session)
    changed = edited_point(session, fiber, 0, [-0.3, 0.1, 1.7])
    before = path(session, fiber)
    session.command("scp.transform", entity=target, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(path(session, fiber)[:, :3], before[:, :3] + [0, 0, 1], atol=1e-12)
    assert session.document.object(fiber).bindings == changed.bindings


def test_cancel_during_edit_restores_geometry_and_binding_field(session):
    target, fiber = moved_fiber(session)
    before, shape = session.document.object(fiber), path(session, fiber)
    session.begin()
    edited_point(session, fiber, 1, [0, 0.6, 1.9])
    session.cancel()
    session.wait()
    assert session.document.object(fiber).attachment_asset == before.attachment_asset
    np.testing.assert_array_equal(path(session, fiber), shape)


def second_surface(session, parent):
    result = session.command("import", path=str(CUBE), units=1.0, parent=parent)
    session.wait()
    key = result["entity_id"]
    session.command("scp.transform", entity=key, values=[3, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    return key


def test_endpoint_candidate_scope_selects_new_parent_only_on_explicit_edit(session):
    target, source = scene(session)
    other = second_surface(session, target)
    fiber = bind(session, target, source)
    retained = edited_point(session, fiber.id, 0, [3, 0, 0.7])
    assert retained.bindings[0].target == target
    session.command(
        "fiber.binding.scope", curve=fiber.id, point=fiber.points[0].id, scope="ANY_PARENT"
    )
    session.wait()
    rebound = edited_point(session, fiber.id, 0, [3, 0.1, 0.7])
    assert rebound.bindings[0].target == other
    assert rebound.bindings[1].target == target


def test_inserted_authored_point_retains_open_endpoint_bindings(session):
    target, fiber = moved_fiber(session)
    before = session.document.object(fiber)
    session.command(
        "curve.point.insert", curve=fiber, index=1, point=dict(position=[-0.2, 0.1, 1.8])
    )
    session.wait()
    changed = session.document.object(fiber)
    assert changed.result.status == "ready", changed.result.error
    assert len(changed.points) == 4 and changed.bindings == before.bindings
    assert changed.edit is None


def test_fiber_consumed_by_body_can_still_edit_without_false_dependency_cycle(session):
    target, fiber = moved_fiber(session)
    body = session.command("primitive.from_curves", curves=[fiber], kind="BODY", parent=target)
    session.wait()
    assert session.document.entity(body).result.asset
    edited_point(session, fiber, 1, [0, 0.4, 1.8])
    assert session.document.entity(body).result.status == "ready"
    assert body not in {s.reference.target for s in session.document.object(fiber).supports}


def test_retained_internal_supports_invalidate_after_capture_changes(session):
    target, source = scene(session)
    other = second_surface(session, target)
    fiber = bind(session, target, source)
    changed = edited_point(session, fiber.id, 1, [3, 0.1, 0.7])
    assert other in {s.reference.target for s in changed.supports}
    assert all(b.target == target for b in changed.bindings)
    session.command("scp.transform", entity=other, values=[3, 0, 0.3, 0, 0, 0, 1, 1, 1])
    session.wait()
    assert session.document.object(fiber.id).result.revision > changed.result.revision
