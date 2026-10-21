"""Final curve placement is owned asynchronous authoring with original gesture history."""

import numpy as np

from tests.test_fiber_creation import scene


def confirm(session, target, curve):
    point = session.document.object(curve).points[1]
    return session.command(
        "surface.snap.curves",
        components=[dict(curve=curve, point=point.id, part="position")],
        targets=[target],
        origin=[0, 0.25, 2],
        direction=[0, 0, -1],
        offset=0.01,
    )


def test_confirmation_publishes_once_and_undo_restores_gesture(session):
    target, curve = scene(session)
    before, cursor = session.document.object(curve), session.history.cursor
    job = confirm(session, target, curve)
    session.wait()
    task = session.scheduler.registry.by_id[job]
    assert task.state == "succeeded", task.error
    assert not task.obsolete
    assert_location(session, curve)
    assert session.history.cursor == cursor + 1
    session.navigate(-1)
    assert session.document.object(curve).points == before.points
    session.navigate(1)
    session.wait()
    assert_location(session, curve)


def assert_location(session, curve):
    np.testing.assert_allclose(
        session.document.object(curve).points[1].position, [0, 0.25, 0.51], atol=1e-6
    )


def test_cancelled_gesture_never_publishes_confirmation(session):
    target, curve = scene(session)
    before = session.document.object(curve)
    session.begin()
    confirm(session, target, curve)
    session.cancel()
    session.wait()
    assert session.document.object(curve).points == before.points


def test_confirmation_preserves_unrelated_later_edits(session):
    target, curve = scene(session)
    confirm(session, target, curve)
    session.command("object.rename", target=curve, name="Renamed during placement")
    session.wait()
    item = session.document.object(curve)
    assert item.name == "Renamed during placement"
    np.testing.assert_allclose(item.points[1].position, [0, 0.25, 0.51], atol=1e-6)


def test_later_point_edit_supersedes_pending_placement(session):
    target, curve = scene(session)
    confirm(session, target, curve)
    point = session.document.object(curve).points[1]
    session.command("curve.point.update", curve=curve, point=point.id, position=[2, 3, 4])
    session.wait()
    assert session.document.object(curve).points[1].position == (2, 3, 4)
    session.navigate(-1)
    session.wait()
    assert_location(session, curve)


def test_changed_target_restarts_capture_and_undo_recovers_previous_target(session):
    target, curve = scene(session)
    confirm(session, target, curve)
    session.command("scp.transform", entity=target, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(
        session.document.object(curve).points[1].position, [0, 0.25, 0.71], atol=1e-6
    )
    session.navigate(-1)
    session.wait()
    assert_location(session, curve)


def test_moving_transform_parent_does_not_double_apply_snap_displacement(session):
    target, curve = scene(session)
    session.command("object.reparent", target=curve, parent=target)
    session.wait()
    confirm(session, target, curve)
    session.command("scp.transform", entity=target, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(
        session.document.object(curve).points[1].position, [0, 0.25, 0.51], atol=1e-6
    )
