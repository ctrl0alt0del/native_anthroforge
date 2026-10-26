"""Envelope publication belongs to its initiating undo action and owned project revision."""

import json

from anthroforge.application import skin_evaluation, storage
from tests.conftest import CUBE


def imported(session, monkeypatch):
    monkeypatch.setattr(skin_evaluation, "TARGET_RESOLUTION", 24)
    entity = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    return entity


def build(session):
    key = session.command("skin.envelope.build")
    session.wait()
    job = session.scheduler.registry.by_id[key]
    assert job.state == "succeeded", job.error
    stage = session.document.skin.envelope
    assert stage.asset in session.assets and stage.data in session.resources.skin
    return stage


def test_envelope_build_undo_redo_and_binding_ownership(session, monkeypatch):
    imported(session, monkeypatch)
    before = session.document
    stage = build(session)
    data = session.resources.skin[stage.data]
    metadata = json.loads(data.metadata)
    assert metadata["resolution"] == 24
    assert data.arrays["source_vertices"].shape == (8, 3)
    assert len(data.arrays["weights"]) == session.assets[stage.asset].mesh.counts[0]
    session.command("undo")
    assert session.document.skin == before.skin
    session.command("redo")
    session.wait()
    assert session.document.skin.envelope == stage


def test_envelope_roundtrip_without_startup_rebuild(session, monkeypatch, tmp_path):
    imported(session, monkeypatch)
    stage = build(session)
    path = tmp_path / "skin.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    document, resources = storage.read_package(path, session.engine)
    assert document.skin.envelope == stage
    assert resources.skin[stage.data].digest == session.resources.skin[stage.data].digest
    assert resources.meshes[stage.asset].mesh.counts == session.assets[stage.asset].mesh.counts


def test_failed_rebuild_keeps_accepted_envelope(session, monkeypatch):
    imported(session, monkeypatch)
    stage = build(session)
    monkeypatch.setattr("anthroforge.application.worker_memory.budget", lambda: 100)
    key = session.command("skin.envelope.build")
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "failed"
    assert session.document.skin.envelope == stage
    assert stage.asset in session.assets and stage.data in session.resources.skin
