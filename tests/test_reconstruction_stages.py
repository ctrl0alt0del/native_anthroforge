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


def test_tissue_stage_comparison_uses_material_domain_not_whole_stage_record(session):
    from tests.test_tissue_workflow import assembly

    _, _, target = assembly(session)
    session.command(
        "reconstruction.compare.start",
        subject=target,
        before=dict(stage="rest"),
        after=dict(stage="final"),
    )
    state = session.command("reconstruction.compare.status", wait=True)
    assert state["state"] == "ready", state
    assert state["report"]["distances"]["material"] is not None


def test_comparison_bounds_frame_paths_and_points_through_native_query(session):
    from anthroforge.native import scene

    frame = session.engine.transform([2, 3, 4, 0, 0, 0, 1, 1, 1])
    result = scene.boxes(session.engine, [[0, 0, 0, 1, 2, 3], [0] * 6], [frame, frame])
    assert result == [2, 3, 4, 3, 5, 7]


def test_fiber_stage_excludes_support_bone_construction(session):
    from anthroforge.application.reconstruction_views import capture
    from tests.test_fiber_creation import bind
    from tests.test_surface_workflow import curve, surface

    bone = session.command("primitive.create", kind="BODY")
    session.wait()
    sources = [bind(session, bone, curve(session, y)).id for y in (0, 0.4)]
    tissue = session.command("tissue.create", source=surface(session, sources, strips=6))
    session.wait()
    layers = capture(session, tissue, "fibers").layers
    assert {row.identity for row in layers} == set(sources)


def test_saved_stage_preserves_geometry_origin_offset(session, assembly, tmp_path):
    from dataclasses import replace

    from anthroforge.application.reconstruction_views import capture

    target = assembly[1]
    item = replace(session.document.entity(target), geometry_offset=(2, 3, 4))
    session.replace_entities({target: item})
    before = capture(session, target).layers[0].frame
    source = tmp_path / "offset.anthroforge"
    session.command("save", path=str(source), blocked_policy="wait")
    row = import_saved_stage(session, target, source)
    assert capture(session, target, row["id"]).layers[0].frame == before


def import_saved_stage(session, target, source):
    row = session.command(
        "reconstruction.stage.import_project",
        subject=target,
        source_entity=target,
        stage="ORIGINAL",
        path=str(source),
    )
    session.wait()
    assert session.scheduler.registry.by_id[row["job_id"]].state == "succeeded"
    return row
