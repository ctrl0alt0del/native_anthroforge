"""Direct engine changes preserve authored construction and ordinary task/history policies."""

from threading import Event

import numpy as np
import pytest

from anthroforge.application import curve_edit_state, path_tasks
from tests.test_curve_conversion import source
from tests.test_fiber_creation import bind, scene
from tests.test_junction_workflow import reference


@pytest.mark.parametrize("closed", [False, True])
def test_engine_switches_keep_all_authored_points_and_one_undo(session, closed):
    session.command("preferences.set", routing_conversion_points="ALL_POINTS")
    key = source(session, closed)
    for engine in ("ROUTED", "POLYLINE", "BEZIER"):
        before, cursor = session.document.object(key), session.history.cursor
        session.command("curve.engine", curve=key, engine=engine)
        assert session.document.object(key).engine == engine
        session.wait()
        item = session.document.object(key)
        assert item.result.status == "ready", item.result.error
        assert item.points == before.points and item.closed == closed
        assert session.history.cursor == cursor + 1
        replay_switch(session, key, before)


def replay_switch(session, key, before):
    session.command("undo")
    assert session.document.object(key).engine_settings == before.engine_settings
    session.command("redo")
    session.wait()


def test_same_engine_and_invalid_engine_leave_document_history_and_jobs_unchanged(session):
    key = source(session)
    before, cursor, jobs = session.document, session.history.cursor, len(session.scheduler.jobs)
    session.command("curve.engine", curve=key, engine="BEZIER")
    with pytest.raises(ValueError):
        session.command("curve.engine", curve=key, engine="UNKNOWN")
    assert session.document == before and session.history.cursor == cursor
    assert len(session.scheduler.jobs) == jobs


def test_engine_change_checks_shared_consumer_topology_and_unlocks(session):
    key = source(session)
    consumer = session.command("primitive.from_curves", curves=[key], kind="BODY")
    child = session.command("scp.empty", name="Attached child", parent=consumer)
    session.wait()
    cursor = session.history.cursor
    with pytest.raises(ValueError, match=child):
        session.command("curve.engine", curve=key, engine="POLYLINE")
    assert session.document.object(key).engine == "BEZIER" and session.history.cursor == cursor
    session.command("scp.delete", entity=child)
    session.command("curve.engine", curve=key, engine="POLYLINE")
    session.wait()
    assert session.document.entity(consumer).result.status == "ready"


def test_manual_engine_change_retains_accepted_path_until_explicit_evaluation(session):
    key = source(session)
    session.command("update_mode", entity=key, mode="MANUAL")
    accepted = session.document.object(key).result.asset
    session.command("curve.engine", curve=key, engine="POLYLINE")
    session.wait()
    item = session.document.object(key)
    assert item.engine == "POLYLINE" and item.result.status == "pending"
    assert item.result.asset == accepted
    session.command("curve.evaluate", curve=key)
    session.wait()
    assert session.document.object(key).result.status == "ready"
    assert session.document.object(key).result.asset != accepted


@pytest.mark.parametrize("engine", ["POLYLINE", "ROUTED"])
def test_fiber_engine_change_uses_resolved_points_without_rebinding(session, engine):
    session.command("preferences.set", routing_conversion_points="ALL_POINTS")
    target, original = scene(session)
    fiber = bind(session, target, original)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    before = curve_edit_state.current(session, session.document.object(fiber.id))
    session.command("curve.engine", curve=fiber.id, engine=engine)
    session.wait()
    after = curve_edit_state.current(session, session.document.object(fiber.id))
    assert after.result.status == "ready", after.result.error
    assert after.bindings == before.bindings and point_ids(after) == point_ids(before)
    np.testing.assert_allclose(
        [p.position for p in after.points], [p.position for p in before.points]
    )


def point_ids(curve):
    return tuple(point.id for point in curve.points)


def test_engine_change_preserves_explicit_junctions(session):
    a, b = source(session), source(session)
    joint = session.command(
        "junction.create", source=reference(session, a), targets=[reference(session, b)]
    )
    session.wait()
    before = session.document.object(a).points
    session.command("curve.engine", curve=a, engine="ROUTED")
    session.wait()
    after = session.document.object(a)
    assert after.result.status == "ready" and after.points == (before[0], before[-1])
    assert after.points[0].junction == joint


def block_evaluation(monkeypatch):
    original, gate = path_tasks.compute, Event()

    def blocked(*args):
        if args[2][0].object(args[1]).engine == "ROUTED":
            assert gate.wait(5)
        return original(*args)

    monkeypatch.setattr(path_tasks, "compute", blocked)
    return gate


def test_superseded_engine_job_cannot_publish_and_undo_redo_restarts(session, monkeypatch):
    key = source(session)
    gate = block_evaluation(monkeypatch)
    try:
        session.command("curve.engine", curve=key, engine="ROUTED")
        session.scheduler.tick()
        session.command("curve.engine", curve=key, engine="POLYLINE")
        session.command("undo")
        session.command("redo")
    finally:
        gate.set()
    session.wait()
    item = session.document.object(key)
    assert item.engine == "POLYLINE" and item.result.status == "ready"
    assert session.resources.paths[item.result.asset].authored.engine == "POLYLINE"


def fail_evaluation(*args):
    raise ValueError("Controlled path failure")


def test_failed_evaluation_keeps_new_engine_and_last_accepted_path_with_issue(session, monkeypatch):
    key = source(session)
    accepted = session.document.object(key).result.asset
    monkeypatch.setattr(path_tasks, "compute", fail_evaluation)
    session.command("curve.engine", curve=key, engine="ROUTED")
    session.wait()
    item = session.document.object(key)
    assert item.engine == "ROUTED" and item.result.status == "failed"
    assert item.result.asset == accepted and "Controlled path failure" in item.result.error
    issues = session.command("issues.list", filters={"target": key})["records"]
    assert any(row["code"] == "CALCULATION_FAILED" for row in issues)
