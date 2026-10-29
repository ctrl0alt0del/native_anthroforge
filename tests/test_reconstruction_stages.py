import json
import zipfile

import pytest

from anthroforge.application import storage


def imported_stage(session, target):
    result = session.command(
        "reconstruction.stage.import_mesh",
        subject=target,
        stage="ORIGINAL",
        path="examples/primitives/cube.obj",
        units=0.001,
    )
    session.wait()
    job = session.scheduler.registry.by_id[result["job_id"]]
    assert job.state == "succeeded", job.error
    return result["id"]


def test_embedded_stage_is_not_anatomy_and_survives_reopen(session, assembly, tmp_path):
    before = session.document.entities
    key = imported_stage(session, assembly[1])
    assert session.document.entities == before
    row = session.document.reconstruction.stages[0]
    path = tmp_path / "embedded.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    document, resources = storage.read_package(path, session.engine)
    assert document.reconstruction.stages[0].id == key
    assert resources.meshes[row.asset].units == 0.001
    session.command("undo")
    assert not session.document.reconstruction.stages
    session.command("redo")
    assert session.document.reconstruction.stages[0].id == key


def test_stage_comparison_distances_do_not_invent_material_lineage(session, assembly):
    target = assembly[1]
    key = imported_stage(session, target)
    session.command(
        "reconstruction.compare.start",
        subject=target,
        before=dict(stage=key),
        after=dict(stage="final"),
        plane=[0, 0, 1, 0],
    )
    state = session.command("reconstruction.compare.status", wait=True)
    assert state["state"] == "ready", state
    assert state["report"]["distances"]["material"] is None
    assert len(state["report"]["sections"]) == 2


def test_review_embeds_evidence_and_protects_stage_history(session, assembly, tmp_path):
    key = imported_stage(session, assembly[1])
    source = tmp_path / "evidence.afinspection.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("inspection.json", json.dumps(dict(test=True)))
    evidence = session.command("reconstruction.evidence.import_file", path=str(source))["id"]
    session.wait()
    review_evidence(session, assembly[1], key, evidence)
    source.unlink()
    with pytest.raises(ValueError, match="history"):
        session.command("reconstruction.stage.remove", stage=key)
    assert session.command("review.inspect")["reviews"][0]["freshness"] == "CURRENT"


def review_evidence(session, subject, stage, evidence):
    session.command(
        "review.set",
        subject=subject,
        dimension="ANATOMY",
        stage=stage,
        decision="APPROVED",
        reviewer="Reviewer",
        evidence=[evidence],
    )
