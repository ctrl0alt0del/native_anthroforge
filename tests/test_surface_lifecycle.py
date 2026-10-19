"""Surface inputs, failure retention, queued creation and Issues share existing lifecycle rules."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import surface_evaluation
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surfaces import Surface
from tests.test_issue_integration import records
from tests.test_path_lifecycle import blocked_paths, point
from tests.test_surface_workflow import curve, surface, vertices


def test_surface_creation_waits_for_queued_source_and_undo_redo(session, monkeypatch):
    gate = blocked_paths(monkeypatch)
    a, b = [session.command("curve.create") for _ in range(2)]
    job = session.command("surface.create", curves=[a, b])
    assert session.scheduler.registry.by_id[job].active
    assert not any(isinstance(o, Surface) for o in session.document.objects)
    session.command("undo")
    gate.set()
    session.wait()
    session.command("redo")
    session.wait()
    found = [o for o in session.document.objects if isinstance(o, Surface)]
    assert len(found) == 1 and found[0].result.status == "ready"
    assert not session.scheduler.errors


def test_surface_reads_manual_accepted_path_then_tracks_publication(session):
    a, b = curve(session), curve(session, 0.4)
    target = surface(session, [a, b])
    before = vertices(session, target)
    session.command("update_mode", entity=a, mode="MANUAL")
    point(session, a, [0, 0, 0.2])
    session.wait()
    np.testing.assert_array_equal(vertices(session, target), before)
    assert a in session.document.object(target).result.pending
    session.command("evaluate", entities=[target])
    session.wait()
    assert not session.document.object(target).result.pending
    assert not np.array_equal(vertices(session, target), before)


def test_missing_manual_path_fails_creation_without_waiting_forever(session):
    a, b = curve(session), curve(session, 0.4)
    item = session.document.object(a)
    changed = replace(item, update_mode="MANUAL", result=EvaluationResult(status="pending"))
    session.replace_document(
        objects=tuple(changed if o.id == a else o for o in session.document.objects)
    )
    job = session.command("surface.create", curves=[a, b])
    session.wait()
    assert session.scheduler.registry.by_id[job].state == "failed"
    assert "no accepted path" in session.scheduler.registry.by_id[job].error
    assert not any(isinstance(o, Surface) for o in session.document.objects)
    assert not session.scheduler.blocked


def fail_surface(*args):
    raise ValueError("Surface fixture calculation failed")


def test_failed_surface_keeps_geometry_and_has_verified_issue_repair(session, monkeypatch):
    target = surface(session, [curve(session), curve(session, 0.4)])
    accepted = session.document.object(target).result.asset
    with monkeypatch.context() as patch:
        patch.setattr(surface_evaluation, "evaluate", fail_surface)
        session.command("surface.update", target=target, flip=True)
        session.wait()
    item = session.document.object(target)
    assert item.result.asset == accepted and item.result.status == "failed"
    issue = records(session, target=target, code="EVALUATION_FAILED")[0]
    assert issue["kind"] == "SURFACE"
    session.command("issues.fix", identity=issue["id"], name="evaluate")
    session.wait()
    assert not records(session, target=target, code="EVALUATION_FAILED")


def test_manual_surface_issue_repair_uses_shared_evaluation(session):
    target = surface(session, [curve(session), curve(session, 0.4)])
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("surface.update", target=target, flip=True)
    session.wait()
    issue = records(session, target=target, code="OUTPUT_PENDING")[0]
    session.command("issues.fix", identity=issue["id"], name="evaluate")
    session.wait()
    assert not records(session, target=target, code="OUTPUT_PENDING")
    assert session.command("issues.repairs")[-1]["state"] == "DONE"


def test_surface_rejects_mixed_closure_and_patch_of_open_curve(session):
    a, b = curve(session), curve(session, 0.4, closed=True)
    with pytest.raises(ValueError, match="closure"):
        session.command("surface.create", curves=[a, b])
    with pytest.raises(ValueError, match="closure"):
        session.command("surface.create", curves=[a], kind="PATCH")
