"""Final repair, timing and empty-anatomy behavior run through the shared coordinator."""

from dataclasses import replace

import pytest

from anthroforge.application import skin_deformation_evaluation, skin_stages
from anthroforge.core.skin import FittedShortcut
from anthroforge.core.skin_pipeline import RepairRequired
from anthroforge.desktop.skin_scene import displayed
from tests.test_skin_automatic_pipeline import (
    final_outputs,
    mock_final_pipeline,
    move,
    pipeline_jobs,
)
from tests.test_skin_jobs import imported


def ready_final(session, monkeypatch):
    owner = imported(session, monkeypatch)
    calls = []
    mock_final_pipeline(monkeypatch, calls)
    session.command("skin.update_mode", mode="FINAL")
    session.wait()
    return owner, calls


@pytest.mark.parametrize("mode", ["LIVE", "ON_RELEASE"])
def test_final_follows_project_gesture_policy(session, monkeypatch, mode):
    owner, calls = ready_final(session, monkeypatch)
    session.command("update_mode", mode=mode)
    session.begin()
    move(session, owner, 0.1)
    session.wait()
    assert calls == ["downstream"] + (["deformation"] if mode == "LIVE" else [])
    session.commit()
    session.wait()
    assert calls == ["downstream", "deformation"]


def test_manual_final_waits_for_explicit_evaluation(session, monkeypatch):
    owner, calls = ready_final(session, monkeypatch)
    session.command("update_mode", mode="MANUAL")
    before = session.document.skin
    move(session, owner, 0.1)
    session.wait()
    assert calls == ["downstream"] and session.document.skin.final == before.final
    session.command("skin.evaluate")
    session.wait()
    assert calls == ["downstream", "deformation"]
    assert session.document.skin.envelope == before.envelope


def failed_solve(*args):
    raise ValueError("controlled numerical failure")


def test_numerical_failure_retains_final_without_repair_loop(session, monkeypatch):
    owner, _ = ready_final(session, monkeypatch)
    before = session.document.skin
    monkeypatch.setattr(skin_deformation_evaluation, "evaluate", failed_solve)
    move(session, owner, 0.1)
    session.wait()
    assert session.document.skin.final.asset == before.final.asset
    assert session.document.skin.envelope == before.envelope
    count = len(pipeline_jobs(session))
    for _ in range(5):
        session.scheduler.tick()
    assert len(pipeline_jobs(session)) == count and pipeline_jobs(session)[-1].state == "failed"


def repair_needed(*args):
    raise RepairRequired("construction", "lost material identity")


def install_repair(monkeypatch, calls, previous):
    def repair(engine, document, resources, cancel, options):
        assert document.skin.update_mode == "FINAL"
        assert document.skin.final.asset == previous.final.asset
        calls.append("construction")
        output = skin_stages.envelope(engine, document, resources, cancel, options)
        return output | final_outputs(document, resources)

    policy = replace(skin_stages.POLICIES["construction"], compute=repair)
    monkeypatch.setitem(skin_stages.POLICIES, "construction", policy)
    monkeypatch.setattr(skin_deformation_evaluation, "evaluate", repair_needed)


def retain_fit(session):
    skin = session.document.skin
    fit = FittedShortcut("retained", "shortcut", skin.final.asset, skin.reference, 0)
    session.replace_document(skin=replace(skin, fits=(fit,)))
    return fit


def test_typed_repair_runs_automatically_retaining_final_and_outdating_fits(session, monkeypatch):
    owner, calls = ready_final(session, monkeypatch)
    fit = retain_fit(session)
    before = session.document.skin
    install_repair(monkeypatch, calls, before)
    move(session, owner, 0.1)
    session.wait()
    after = session.document.skin
    assert calls == ["downstream", "construction"]
    assert after.update_mode == "FINAL" and after.envelope != before.envelope
    assert after.final.asset != before.final.asset and after.fits == (replace(fit, stale=True),)
    assert session.command("skin.status")["pipeline"]["phase"] == "current"


def test_last_contributor_removal_hides_draft_but_undo_restores_resources(session, monkeypatch):
    owner = imported(session, monkeypatch)
    previous = displayed(session)
    session.command("scp.delete", entity=owner)
    session.wait()
    state = session.command("skin.status")["pipeline"]
    assert state["label"] == "No contributing anatomy" and not state["can_retry"]
    assert displayed(session) is None and previous.asset in session.assets
    session.command("undo")
    session.wait()
    assert displayed(session) == previous
