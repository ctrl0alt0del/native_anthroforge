"""Bind-time material captures cannot leak from later parent poses into historical state."""

import numpy as np

from anthroforge.application import anchor_capture
from anthroforge.core.fibers import Fiber
from tests.test_creation_invalidation import create, hold
from tests.test_fiber_creation import path


def moved_capture(session, monkeypatch):
    parent = session.command("import", path="examples/primitives/cube.obj", units=1.0)["entity_id"]
    session.wait()
    point = session.command("construction.point.create", position=[0, 0, 0.7])
    _, release = hold(monkeypatch, anchor_capture)
    anchor = session.command("anchor.create", source=point, parent=parent)["object_id"]
    origin = session.history.cursor
    try:
        session.command("scp.transform", entity=parent, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    finally:
        release.set()
    session.wait()
    return anchor, origin


def test_anchor_history_recaptures_against_its_own_inputs(session, monkeypatch):
    anchor, origin = moved_capture(session, monkeypatch)
    assert anchor not in session.history.entries[origin].document.registry.records
    np.testing.assert_allclose(session.document.object(anchor).resolved_position, [0, 0, 0.7])
    session.navigate(-1)
    session.wait()
    np.testing.assert_allclose(session.document.object(anchor).resolved_position, [0, 0, 0.7])
    session.navigate(1)
    session.wait()
    np.testing.assert_allclose(session.document.object(anchor).resolved_position, [0, 0, 0.7])


def test_fiber_history_preserves_shape_after_parent_motion_during_capture(session, monkeypatch):
    from anthroforge.application import fiber_tasks

    source, request, _ = create(session, "fiber")
    _, release = hold(monkeypatch, fiber_tasks)
    request()
    parent = session.document.entities[0].id
    session.command("scp.transform", entity=parent, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    release.set()
    session.wait()
    fiber = next(item for item in session.document.objects if isinstance(item, Fiber))
    session.navigate(-1)
    session.wait()
    np.testing.assert_allclose(path(session, fiber.id), path(session, source), atol=1e-10)
    verify_future_fiber_capture(session, fiber.id, source, parent)


def verify_future_fiber_capture(session, fiber, source, parent):
    session.navigate(1)
    session.wait()
    session.command("scp.transform", entity=parent, values=[0, 0, 1.1, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(
        path(session, fiber)[:, :3], path(session, source)[:, :3] + [0, 0, 0.1], atol=1e-10
    )
