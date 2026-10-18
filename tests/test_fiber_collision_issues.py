"""Collision evidence is advisory, revision-aware and engine preserving."""

from threading import Event

import numpy as np
import pytest

from anthroforge.application.issues import fiber_collisions
from tests.test_fiber_creation import CUBE, bind, path


def scene(session, engine="POLYLINE"):
    target = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    source = session.command(
        "curve.create", engine=engine, points=[dict(position=[x, 0, 0]) for x in (-1, 1)]
    )
    session.wait(5)
    return target, bind(session, target, source)


def collisions(session):
    return session.command("issues.list", filters=dict(code="FIBER_COLLISION"))["records"]


@pytest.mark.parametrize("engine", ["BEZIER", "POLYLINE"])
def test_authored_fiber_reports_collision_without_rerouting(session, engine):
    target, fiber = scene(session, engine)
    before, revision, undo = (
        path(session, fiber.id),
        session.document.revision,
        session.history.cursor,
    )
    session.command("issues.recheck", provider="fiber_collisions.v1")
    session.wait(5)
    rows = collisions(session)
    assert len(rows) == 1 and rows[0]["target"] == fiber.id and target in rows[0]["related"]
    assert rows[0]["freshness"] == "current" and rows[0]["evidence"]["segment"] >= 0
    np.testing.assert_array_equal(path(session, fiber.id), before)
    assert session.document.object(fiber.id).engine == engine
    assert session.document.revision == revision and session.history.cursor == undo


def test_independent_obstacle_motion_refreshes_findings(session):
    target, fiber = scene(session)
    obstacle = session.command("import", path=str(CUBE), units=1.0, parent=target)["entity_id"]
    session.wait(5)
    assert len(collisions(session)) == 2
    session.command("scp.transform", entity=obstacle, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    rows = collisions(session)
    assert len(rows) == 1 and rows[0]["related"] == (target,)
    assert session.document.object(fiber.id).engine == "POLYLINE"


def test_collision_provider_releases_removed_fiber_findings(session):
    _, fiber = scene(session)
    assert collisions(session)
    session.command("object.delete", target=fiber.id)
    session.wait(5)
    assert not collisions(session)


def hold_query(monkeypatch):
    entered, release = Event(), Event()
    original = fiber_collisions.query

    def query(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(fiber_collisions, "query", query)
    return entered, release


def start_check(session, entered):
    session.command("issues.recheck", provider=fiber_collisions.NAME)
    session.scheduler.tick()
    assert entered.wait(2)
    return session.issues.listening.running[fiber_collisions.NAME]


def test_cancelled_collision_job_cannot_publish_or_block_save(session, monkeypatch, tmp_path):
    scene(session)
    entered, release = hold_query(monkeypatch)
    job = start_check(session, entered)
    try:
        assert not session.scheduler.blocked
        session.command("save", path=str(tmp_path / "fiber.anthroforge"), blocked_policy="wait")
        session.command("issues.cancel", provider=fiber_collisions.NAME)
        assert job.cancel.is_set()
    finally:
        release.set()
    session.wait(5)
    assert all(row["freshness"] != "current" for row in collisions(session))


def test_stale_collision_capture_is_rechecked(session, monkeypatch):
    target, _ = scene(session)
    obstacle = session.command("import", path=str(CUBE), units=1.0, parent=target)["entity_id"]
    session.wait(5)
    entered, release = hold_query(monkeypatch)
    start_check(session, entered)
    try:
        session.command("scp.transform", entity=obstacle, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    finally:
        release.set()
    session.wait(5)
    rows = collisions(session)
    assert len(rows) == 1 and rows[0]["related"] == (target,)
    assert rows[0]["freshness"] == "current"
