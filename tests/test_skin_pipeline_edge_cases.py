"""Mode handoff, retry intent and status remain independent of pending UI settings."""

from dataclasses import replace

import pytest

from anthroforge.application import skin_builder_configuration as builders
from anthroforge.application import skin_evaluation
from tests.test_skin_automatic_pipeline import hold_draft, move, pipeline_jobs
from tests.test_skin_jobs import imported


def test_status_observers_do_not_mutate_authored_state_or_submit_work(session, monkeypatch):
    imported(session, monkeypatch)
    before = session.document, session.history.cursor, tuple(pipeline_jobs(session))
    for _ in range(5):
        state = session.command("skin.status")["pipeline"]
        assert state["mode"] == "DRAFT" and state["draft"] == "ready"
    assert before == (session.document, session.history.cursor, tuple(pipeline_jobs(session)))


def test_final_request_waits_for_inflight_draft(session, monkeypatch):
    owner = imported(session, monkeypatch)
    entered, release = hold_draft(monkeypatch)
    move(session, owner, 0.1)
    session.scheduler.tick()
    assert entered.wait(5)
    try:
        session.command("skin.update_mode", mode="FINAL")
        assert session.document.skin.update_mode == "FINAL"
        assert all(j.kind == "skin_envelope" for j in session.skin_pipeline.active())
        assert session.command("skin.status")["pipeline"]["stage"] == "envelope"
    finally:
        release.set()


def fail(request):
    raise ValueError("controlled numerical failure")


def failed_automatic(session, monkeypatch):
    owner = imported(session, monkeypatch)
    builder = skin_evaluation.BUILDERS["FIELD"]
    monkeypatch.setitem(skin_evaluation.BUILDERS, "FIELD", replace(builder, build=fail))
    move(session, owner, 0.1)
    session.wait()
    assert pipeline_jobs(session)[-1].state == "failed"
    return builder


def test_retry_does_not_apply_parameters_edited_after_automatic_failure(session, monkeypatch):
    builder = failed_automatic(session, monkeypatch)
    session.command("skin.configure", section="envelope_settings", values=dict(gap_strength=0.2))
    monkeypatch.setitem(skin_evaluation.BUILDERS, "FIELD", builder)
    session.command("skin.retry")
    session.wait()
    assert pipeline_jobs(session)[-1].state == "succeeded"
    applied = builders.projected(session.document, builders.automatic(session.document.skin))
    assert builders.decode(applied.skin).settings.gap_strength == 1
    assert builders.decode(session.document.skin).settings.gap_strength == 0.2


def test_repeated_repair_without_effective_input_change_is_reported(session, monkeypatch):
    imported(session, monkeypatch)
    runtime = session.skin_pipeline
    runtime.require_repair("construction", "lost material")
    with pytest.raises(ValueError, match="no progress"):
        runtime.require_repair("construction", "lost material")
    runtime.invalidate()
    runtime.require_repair("construction", "lost material")
