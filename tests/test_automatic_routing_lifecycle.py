"""Automatic inputs retain Manual provenance, dispatch safety and workspace independence."""

from dataclasses import replace
from threading import Event

from anthroforge.application import routing_evaluation
from anthroforge.core.results import EvaluationResult
from anthroforge.core.routing_obstacles import targets
from tests.test_automatic_routing import cube, curve, ready


def body(session):
    key = session.command("primitive.create", kind="BODY")
    session.wait(10)
    return key


def test_automatic_route_uses_manual_accepted_surface_then_refreshes(session):
    obstacle = body(session)
    key = curve(session)
    session.command("update_mode", entity=obstacle, mode="MANUAL")
    piece = session.document.entity(obstacle).primitive.pieces[0].id
    session.command("body.update", entity=obstacle, piece=piece, width=0.6)
    pending = ready(session, key)
    assert obstacle in pending.result.pending
    accepted = next(
        r for r in pending.result.inputs if r.owner == obstacle and r.output == "geometry"
    )
    session.command("evaluate", entities=[obstacle])
    result = ready(session, key).result
    current = next(r for r in result.inputs if r.owner == obstacle and r.output == "geometry")
    assert not result.pending and current.accepted > accepted.accepted


def test_missing_manual_surface_fails_and_retains_previous_output(session):
    obstacle = body(session)
    key = curve(session)
    previous = ready(session, key).result.asset
    item = session.document.entity(obstacle)
    session.replace_entities(
        {obstacle: replace(item, asset="", result=EvaluationResult(), update_mode="MANUAL")}
    )
    session.command("curve.evaluate", curve=key)
    session.wait(10)
    result = session.document.object(key).result
    assert result.status == "failed" and result.asset == previous
    assert "accepted" in result.error.lower() or "dependency" in result.error.lower()
    assert not session.scheduler.blocked


def block_routing(monkeypatch):
    original, gate, started = routing_evaluation.evaluate, Event(), Event()

    def blocked(*args, **kwargs):
        started.set()
        assert gate.wait(5)
        return original(*args, **kwargs)

    monkeypatch.setattr(routing_evaluation, "evaluate", blocked)
    return gate, started


def dispatch(session, key):
    session.command("curve.evaluate", curve=key)
    job = next(j for j in session.scheduler.active_jobs if j.key == "path:" + key)
    job.ready_at = 0
    session.scheduler.tick()
    return job


def test_new_surface_supersedes_running_capture_and_registers_fresh_inputs(session, monkeypatch):
    root = cube(session)
    key = curve(session)
    gate, started = block_routing(monkeypatch)
    try:
        obsolete = dispatch(session, key)
        assert started.wait(2)
        new = session.command("primitive.create", kind="BODY", parent=root)
    finally:
        gate.set()
    item = ready(session, key)
    assert obsolete.state == "obsolete" and set(targets(session.document, item)) == {root, new}
    assert next(r for r in item.result.inputs if r.output == "routing_scope").membership


def test_workspace_visibility_does_not_remove_physical_obstacles(session):
    root = cube(session)
    other = cube(session, parent=root, y=4)
    key = curve(session, owner=root)
    session.command("workspace.create", name="Other only", members=[other], children=False)
    session.command("workspace.update", hidden_categories=["geometry"])
    before = targets(session.document, session.document.object(key))
    session.command("scp.transform", entity=other, values=[0, 0, 0, 0, 0, 0, 1, 1, 1])
    item = ready(session, key)
    assert set(before) == set(targets(session.document, item)) == {root, other}
    assert session.priority({key}) == 0
