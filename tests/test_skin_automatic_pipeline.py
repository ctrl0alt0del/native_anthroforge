"""Committed Draft updates and exclusive Final work share publication and history."""

from dataclasses import asdict, replace
from threading import Event

import numpy as np
import pytest

from anthroforge.application import skin_assets, skin_evaluation, skin_stages, storage
from anthroforge.application import skin_builder_configuration as builders
from anthroforge.application.skin_results import ComputedStage
from anthroforge.core.skin_sources import contributors
from tests.test_skin_jobs import imported


def move(session, owner, amount):
    session.command("scp.transform", entity=owner, values=[amount, 0, 0, 0, 0, 0, 1, 1, 1])


def pipeline_jobs(session):
    return [j for j in session.scheduler.jobs if j.kind.startswith("skin_")]


def test_initial_draft_is_automatic_and_belongs_to_import_undo(session, monkeypatch):
    imported(session, monkeypatch)
    accepted = session.document.skin
    assert accepted.envelope.asset and accepted.applied_draft.configuration.builder == "FIELD"
    assert not accepted.topology.asset and not accepted.final.asset
    assert not pipeline_jobs(session)[0].user_cancelable
    session.command("undo")
    assert not session.document.skin.envelope.asset
    session.command("redo")
    session.wait()
    assert session.document.skin == accepted


def test_draft_waits_for_commit_and_uses_applied_parameters(session, monkeypatch):
    owner = imported(session, monkeypatch)
    previous = session.document.skin.envelope
    session.command("skin.configure", section="envelope_settings", values=dict(gap_strength=0.2))
    session.command("begin")
    move(session, owner, 0.1)
    session.scheduler.tick()
    assert session.document.skin.envelope == previous and not session.skin_pipeline.active()
    session.command("commit")
    session.wait()
    assert session.document.skin.envelope != previous
    applied = builders.projected(session.document, builders.automatic(session.document.skin))
    assert builders.decode(applied.skin).settings.gap_strength == 1
    assert builders.decode(session.document.skin).settings.gap_strength == 0.2


def hold_draft(monkeypatch):
    entered, release = Event(), Event()
    original = skin_stages.POLICIES["envelope"]

    def compute(*arguments):
        entered.set()
        assert release.wait(10)
        return original.compute(*arguments)

    monkeypatch.setitem(skin_stages.POLICIES, "envelope", replace(original, compute=compute))
    return entered, release


def test_user_cannot_cancel_automatic_draft_through_generic_api(session, monkeypatch):
    owner = imported(session, monkeypatch)
    entered, release = hold_draft(monkeypatch)
    move(session, owner, 0.2)
    session.scheduler.tick()
    assert entered.wait(5)
    try:
        job = session.skin_pipeline.active()[0]
        with pytest.raises(ValueError, match="cannot be cancelled"):
            session.command("job.cancel", job_id=job.id, obsolete=True)
    finally:
        release.set()
    session.wait()
    assert job.state == "succeeded"


def fail_builder(request):
    raise ValueError("fixture builder unavailable")


def test_failed_builder_selection_falls_back_to_last_applied_on_next_edit(session, monkeypatch):
    owner = imported(session, monkeypatch)
    previous = session.document.skin.envelope
    avbd = replace(skin_evaluation.BUILDERS["AVBD"], build=fail_builder)
    monkeypatch.setitem(skin_evaluation.BUILDERS, "AVBD", avbd)
    session.command("skin.configure", section="draft_settings", values=dict(backend="AVBD"))
    session.wait()
    assert session.document.skin.envelope == previous
    assert len(pipeline_jobs(session)) == 2 and pipeline_jobs(session)[-1].state == "failed"
    move(session, owner, 0.3)
    session.wait()
    assert session.document.skin.envelope != previous
    assert session.document.skin.applied_draft.configuration.builder == "FIELD"
    assert session.document.skin.draft_settings.backend == "AVBD"


def final_outputs(document, resources):
    rows = contributors(document)
    source_keys = tuple(document.object(r.owner).result.asset for r in rows)
    mesh = resources.meshes[source_keys[0]].mesh
    metadata = dict(sources=[asdict(r) for r in rows], tissue_surface="FINISHED")
    reference = skin_assets.create(dict(vertex_ids=np.arange(mesh.counts[0])), metadata)
    topology = ComputedStage(mesh, skin_assets.create({}, metadata))
    data = skin_assets.create({}, dict(reference=reference.digest))
    return dict(topology=topology, final=ComputedStage(mesh, data, reference, source_keys))


def mock_final_pipeline(monkeypatch, calls):
    def downstream(engine, document, resources, cancel, options):
        calls.append("downstream")
        return final_outputs(document, resources)

    def deform(engine, document, resources, cancel):
        calls.append("deformation")
        data = skin_assets.create({}, dict(reference=document.skin.reference))
        return ComputedStage(resources.meshes[document.skin.final.asset].mesh, data)

    policy = replace(skin_stages.POLICIES["downstream"], compute=downstream)
    monkeypatch.setitem(skin_stages.POLICIES, "downstream", policy)
    monkeypatch.setattr("anthroforge.application.skin_deformation_evaluation.evaluate", deform)


def test_mode_switch_preserves_draft_during_final_deformation(session, monkeypatch):
    owner = imported(session, monkeypatch)
    calls = []
    mock_final_pipeline(monkeypatch, calls)
    draft = session.document.skin.envelope
    session.command("skin.update_mode", mode="FINAL")
    session.wait()
    assert calls == ["downstream"] and session.document.skin.envelope == draft
    move(session, owner, 0.3)
    session.wait()
    assert calls == ["downstream", "deformation"] and session.document.skin.envelope == draft
    session.command("skin.update_mode", mode="DRAFT")
    session.wait()
    assert session.document.skin.envelope != draft


def test_opening_saved_project_does_not_start_automatic_skin_jobs(session, monkeypatch, tmp_path):
    owner = imported(session, monkeypatch)
    saved = tmp_path / "mode.anthroforge"
    storage.atomic_save(saved, session.document, session.resources)
    previous = session.document.skin
    session.command("open", path=str(saved))
    session.wait()
    assert session.document.skin == previous and not pipeline_jobs(session)
    move(session, owner, 0.5)
    session.wait()
    assert session.document.skin.envelope != previous.envelope


def hold_final(monkeypatch):
    entered, release = Event(), Event()

    def downstream(engine, document, resources, cancel, options):
        entered.set()
        assert release.wait(10)
        return final_outputs(document, resources)

    policy = replace(skin_stages.POLICIES["downstream"], compute=downstream)
    monkeypatch.setitem(skin_stages.POLICIES, "downstream", policy)
    return entered, release


def test_switching_to_draft_rejects_late_final_publication(session, monkeypatch):
    imported(session, monkeypatch)
    entered, release = hold_final(monkeypatch)
    session.command("skin.update_mode", mode="FINAL")
    session.scheduler.tick()
    assert entered.wait(5)
    try:
        session.command("skin.update_mode", mode="DRAFT")
    finally:
        release.set()
    session.wait()
    assert session.document.skin.update_mode == "DRAFT"
    assert not session.document.skin.final.asset and not session.document.skin.topology.asset
    assert pipeline_jobs(session)[-1].state == "obsolete"


def test_parameter_edit_during_build_remains_pending(session, monkeypatch):
    owner = imported(session, monkeypatch)
    entered, release = hold_draft(monkeypatch)
    move(session, owner, 0.2)
    session.scheduler.tick()
    assert entered.wait(5)
    try:
        configure_pending_gap(session)
    finally:
        release.set()
    session.wait()
    applied = builders.projected(session.document, builders.automatic(session.document.skin))
    assert builders.decode(applied.skin).settings.gap_strength == 1
    assert builders.decode(session.document.skin).settings.gap_strength == 0.3


def configure_pending_gap(session):
    session.command("skin.configure", section="envelope_settings", values=dict(gap_strength=0.3))
