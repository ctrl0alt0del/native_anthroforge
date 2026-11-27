"""The selected draft generator shares source binding, publication and authored history."""

import json
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import (
    skin_avbd,
    skin_capture,
    skin_codec,
    skin_evaluation,
    skin_inputs,
    storage,
)
from anthroforge.application.construction_policy import revisions
from anthroforge.application.skin_avbd_capture import indexed_surfaces, stage_lists
from anthroforge.application.skin_draft_build import DraftBuilder
from anthroforge.core.results import Port
from tests.test_skin_jobs import build, imported
from tests.test_tissue_workflow import assembly as tissue_assembly


def choose(session, backend, **settings):
    session.command(
        "skin.configure", section="draft_settings", values=dict(backend=backend, **settings)
    )


def check_builder_result(request):
    table = indexed_surfaces(request.capture)
    order, tissues = stage_lists(request.document, table, {})
    assert not tissues and order[0]["id"] in table
    source = request.capture.sources[0]
    return source.mesh, dict(quality={}, observed=order)


def test_opt_in_is_persisted_and_field_survives_switch(session, monkeypatch, tmp_path):
    imported(session, monkeypatch)
    assert skin_codec.decode({}).draft_settings.backend == "FIELD"
    field = build(session)
    monkeypatch.setitem(skin_evaluation.BUILDERS, "AVBD", DraftBuilder(1, check_builder_result))
    choose(session, "AVBD")
    assert session.document.skin.envelope == field
    avbd = build(session)
    info = session.resources.skin[avbd.data]
    assert json.loads(info.metadata)["builder"] == "AVBD"
    assert len(info.arrays["weights"]) == session.assets[avbd.asset].mesh.counts[0]
    saved = tmp_path / "chosen.anthroforge"
    storage.atomic_save(saved, session.document, session.resources)
    restored, _ = storage.read_package(saved, session.engine)
    assert restored.skin == session.document.skin


def test_unavailable_worker_keeps_accepted_draft_and_selection(session, monkeypatch, tmp_path):
    imported(session, monkeypatch)
    previous = build(session)
    monkeypatch.setenv("ANTHROFORGE_AVBD_RUNTIME", str(tmp_path))
    choose(session, "AVBD")
    job = session.command("skin.envelope.build")
    session.wait()
    error = session.scheduler.registry.by_id[job]
    assert error.state == "failed" and "runtime unavailable" in error.error
    assert session.document.skin.envelope == previous
    choose(session, "FIELD")
    assert json.loads(session.resources.skin[build(session).data].metadata)["builder"] == "FIELD"


def test_plan_import_is_owned_and_revisions_follow_selected_builder(session, tmp_path):
    bone, _, tissue = tissue_assembly(session)
    previous = session.document
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(dict(bones=[dict(id=bone)], muscles=[dict(id=tissue, frames=40)])))
    choose(session, "AVBD")
    session.command("skin.draft.plan.import", path=str(f))
    f.unlink()
    document = session.document
    assert json.loads(document.skin.draft_settings.plan)["muscles"][0]["frames"] == 40
    assert Port(tissue, "base") in skin_inputs.envelope(document)
    p = Port(str(document.id), "skin_envelope_settings")
    assert revisions(previous, {p}) != revisions(document, {p})
    session.command("undo")
    assert session.document.skin.draft_settings.plan == "{}"


def test_explicit_plan_cannot_silently_drop_a_bone(session, monkeypatch):
    owner = imported(session, monkeypatch)
    previous = build(session)
    choose(session, "AVBD", plan={"bones": [{"id": "another-bone"}]})
    monkeypatch.setattr(skin_avbd, "runtime", lambda: (None, None))
    job = session.command("skin.envelope.build")
    session.wait()
    error = session.scheduler.registry.by_id[job].error
    assert "source mismatch" in error and owner in error and "another-bone" in error
    assert session.document.skin.envelope == previous


def test_newer_unavailable_selection_still_allows_opening_project(session, monkeypatch):
    imported(session, monkeypatch)
    chosen = skin_codec.decode({"draft_settings": {"backend": "FUTURE"}})
    session.replace_document(
        skin=replace(session.document.skin, draft_settings=chosen.draft_settings)
    )
    assert "unavailable" in session.skin_status.snapshot().operations["build"].reason


def test_worker_receipt_and_indices_are_checked_before_publication(tmp_path, session):
    (tmp_path / "result.json").write_text(
        json.dumps({"accepted": True, "skin": str(tmp_path.parent)})
    )
    with pytest.raises(ValueError, match="outside"):
        skin_avbd.accepted_path(tmp_path)
    np.zeros((3, 3), "<f8").tofile(tmp_path / "latest.bin")
    np.array([0, 1, 3], "<i4").tofile(tmp_path / "faces.bin")
    with pytest.raises(ValueError, match="triangle index"):
        skin_avbd.mesh_from_output(session.engine, tmp_path)


def test_incomplete_worker_stages_cannot_publish_a_valid_looking_mesh(tmp_path):
    (tmp_path / "recipe.json").write_text(json.dumps({"bones": [{"id": "b"}], "muscles": []}))
    with pytest.raises(ValueError, match="incomplete or out-of-order bones"):
        skin_avbd.validate_stages(tmp_path / "output", [], [], {})


def test_mirrored_bone_gets_distinct_stage_with_reflected_winding(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    session.wait()
    choose(session, "AVBD")
    document = session.document
    table = indexed_surfaces(skin_capture.capture(session.engine, document, session.resources))
    mirror = f"mirror/{root}/{child}"
    rows, _ = stage_lists(document, table, {})
    assert [r["id"] for r in rows] == [root, child, mirror]
    _, points, faces, first = table[child]
    _, mirrored, reversed_faces, offset = table[mirror]
    np.testing.assert_allclose(mirrored[:, 0], 4 - points[:, 0])
    np.testing.assert_allclose(mirrored[:, 1:], points[:, 1:])
    np.testing.assert_array_equal(reversed_faces - offset, (faces - first)[:, ::-1])
