"""Common path results, Manual provenance, failure retention and coordinated history."""

from threading import Event

import numpy as np

from anthroforge.application import path_assets


def curve(session, **options):
    key = session.command("curve.create", **options)
    session.wait(5)
    return key


def point(session, key, position):
    item = session.document.object(key)
    session.command("curve.point.update", curve=key, point=item.points[0].id, position=position)


def path(session, key):
    return session.resources.paths[session.document.object(key).result.asset].path.array()


def vertices(session, key):
    return session.assets[session.document.entity(key).asset].mesh.array(0)


def test_standalone_polyline_path_has_no_anatomical_wrapper(session):
    key = curve(session, engine="POLYLINE")
    assert not session.document.entities
    assert len(path(session, key)) == 2
    item = session.document.object(key)
    assert item.result.status == "ready" and item.result.revision == 1
    assert item.generation == item.construction_revision == 0
    assert any(job.kind == "curve_path" for job in session.scheduler.jobs)


def test_manual_source_stays_accepted_until_explicit_evaluation(session):
    key = curve(session)
    consumer = session.command("primitive.from_curves", kind="BODY", curves=[key])
    session.wait(5)
    before = vertices(session, consumer).copy()
    session.command("update_mode", entity=key, mode="MANUAL")
    point(session, key, [-1, 0.5, 0])
    session.wait(5)
    retained = session.document.entity(consumer)
    np.testing.assert_array_equal(vertices(session, consumer), before)
    assert key in retained.result.pending
    session.command("curve.evaluate", curve=key)
    session.wait(5)
    assert not session.document.entity(consumer).result.pending
    assert not np.array_equal(vertices(session, consumer), before)


def test_on_release_path_edit_retains_output_until_commit(session):
    key = curve(session)
    session.command("update_mode", entity=key, mode="ON_RELEASE")
    previous = path(session, key).copy()
    session.begin()
    point(session, key, [-1, 0.5, 0])
    assert session.document.object(key).result.status == "pending"
    assert not session.scheduler.blocked
    np.testing.assert_array_equal(path(session, key), previous)
    session.commit()
    session.wait(5)
    assert not np.array_equal(path(session, key), previous)


def test_failed_path_retains_previous_result_and_has_typed_issue(session):
    key = curve(session, engine="POLYLINE")
    previous = path(session, key).copy()
    point(session, key, [0.5, 0, 0])
    session.wait(5)
    assert session.document.object(key).result.status == "failed"
    np.testing.assert_array_equal(path(session, key), previous)
    reports = session.command("issues.list", filters={"target": key})["records"]
    assert any(row["kind"] == "CURVE" and row["code"] == "CALCULATION_FAILED" for row in reports)


def blocked_paths(monkeypatch):
    original, gate = path_assets.evaluate, Event()

    def blocked(*args):
        assert gate.wait(5)
        return original(*args)

    monkeypatch.setattr(path_assets, "evaluate", blocked)
    return gate


def test_undo_during_queued_curve_creation_and_redo_restart(session, monkeypatch):
    gate = blocked_paths(monkeypatch)
    key = session.command("curve.create")
    session.scheduler.tick()
    session.command("undo")
    assert not session.document.objects
    session.command("redo")
    gate.set()
    session.wait(5)
    assert session.document.object(key).result.asset
    assert any(job.state == "obsolete" for job in session.scheduler.jobs)


def test_historical_save_keeps_accepted_path_for_its_revision(session, tmp_path):
    key = curve(session)
    before = path(session, key).copy()
    session.command("update_mode", entity=key, mode="MANUAL")
    point(session, key, [-1, 0.5, 0])
    target = tmp_path / "manual.anthroforge"
    session.command("save", path=str(target), blocked_policy="wait")
    session.command("open", path=str(target))
    np.testing.assert_array_equal(path(session, key), before)
    assert session.document.object(key).result.status == "pending"
    assert not session.scheduler.blocked
