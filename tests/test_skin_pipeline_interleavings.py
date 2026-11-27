"""Required Final repairs obey later mode/input intent and retain visible accepted skin."""

from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application import skin_stages
from anthroforge.desktop.skin_scene import displayed
from tests.conftest import CUBE
from tests.test_skin_automatic_pipeline import final_outputs, move, pipeline_jobs
from tests.test_skin_pipeline_repair import ready_final


def hold_repair(monkeypatch):
    entered, release = Event(), Event()

    def compute(engine, document, resources, cancel, options):
        entered.set()
        assert release.wait(10)
        outputs = final_outputs(document, resources)
        return outputs | dict(envelope=outputs["topology"])

    policy = replace(skin_stages.POLICIES["construction"], compute=compute)
    monkeypatch.setitem(skin_stages.POLICIES, "construction", policy)
    return entered, release


def start_repair(session, entered, previous):
    session.command("import", path=str(CUBE), units=1, parent=session.document.entities[0].id)
    for _ in range(100):
        session.scheduler.tick()
        if entered.wait(0.05):
            break
    assert entered.is_set()
    assert displayed(session) == previous.final
    job = session.skin_pipeline.active()[0]
    assert job.kind == "skin_construction" and session.document.skin.update_mode == "FINAL"
    return job


@pytest.mark.parametrize("change", ["mode", "anatomy"])
def test_inflight_required_repair_rejects_obsolete_input_and_mode(session, monkeypatch, change):
    owner, _ = ready_final(session, monkeypatch)
    previous = session.document.skin
    entered, release = hold_repair(monkeypatch)
    job = start_repair(session, entered, previous)
    try:
        change_during_repair(session, change, owner)
    finally:
        release.set()
    session.wait()
    assert job.state == "obsolete" and previous.final.asset in session.assets
    verify_target_after_repair(session, change, previous)


def change_during_repair(session, change, owner):
    if change == "mode":
        session.command("skin.update_mode", mode="DRAFT")
    else:
        move(session, owner, 0.2)


def verify_target_after_repair(session, change, previous):
    skin = session.document.skin
    assert session.command("skin.status")["pipeline"]["phase"] == "current"
    assert skin.envelope != previous.envelope
    if change == "mode":
        assert skin.update_mode == "DRAFT" and skin.final == previous.final
        assert displayed(session) == skin.envelope
    else:
        assert skin.update_mode == "FINAL" and skin.final.asset != previous.final.asset
        assert displayed(session) == skin.final
        assert pipeline_jobs(session)[-1].state == "succeeded"


def test_contributor_add_and_remove_request_required_construction(session, monkeypatch):
    owner, _ = ready_final(session, monkeypatch)
    previous = session.document.skin
    _, release = hold_repair(monkeypatch)
    release.set()
    child = session.command("import", path=str(CUBE), units=1, parent=owner)["entity_id"]
    session.wait()
    added = session.document.skin
    assert added.reference != previous.reference and added.update_mode == "FINAL"
    session.command("scp.delete", entity=child)
    session.wait()
    assert session.document.skin.reference != added.reference
    assert session.document.skin.update_mode == "FINAL"
    assert previous.final.asset in session.assets and added.final.asset in session.assets


@pytest.mark.parametrize("display", ["AUTO", "ENVELOPE", "TOPOLOGY", "FINAL", "NONE"])
def test_mode_changes_preserve_explicit_display_selection(session, monkeypatch, display):
    ready_final(session, monkeypatch)
    session.command("workspace.update", skin_display=display)
    skin = session.document.skin
    expected = dict(AUTO=skin.final, ENVELOPE=skin.envelope, TOPOLOGY=skin.topology)
    expected.update(FINAL=skin.final, NONE=None)
    assert displayed(session) == expected[display]
    session.command("skin.update_mode", mode="DRAFT")
    session.wait()
    expected["AUTO"] = session.document.skin.envelope
    assert session.workspace.skin_display == display and displayed(session) == expected[display]
