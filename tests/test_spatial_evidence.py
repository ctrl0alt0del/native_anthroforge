"""Shared, revision-qualified surface findings never mutate the inspected document."""

from dataclasses import replace

import pytest

from anthroforge.application import inspection_report, inspection_surfaces
from anthroforge.core.skin import SkinStage
from tests.test_tissue_interaction import controller as controller


def crossing(session, tmp_path):
    path = tmp_path / "crossing.obj"
    path.write_text(
        "v -1 -1 0\nv 1 -1 0\nv 0 1 0\nv 0 -.5 -1\nv 0 -.5 1\nv .5 .5 0\nf 1 2 3\nf 4 5 6\n"
    )
    target = session.command("import", path=str(path), units=1)["entity_id"]
    session.wait()
    return target


def finding(session, target):
    session.command("geometry.check", target=target)
    session.wait()
    rows = session.issues.presentation.query({"provider": "surface_geometry.v1"})["records"]
    assert rows, session.issues.presentation.status()
    return next(row for row in rows if row["code"] == "SELF_CROSSING")


def test_shared_check_is_explicit_and_preserves_revision(session, tmp_path):
    target = crossing(session, tmp_path)
    assert not session.issues.presentation.query({"provider": "surface_geometry.v1"})["records"]
    before, cursor = session.document, session.history.cursor
    row = finding(session, target)
    witness = session.command("geometry.finding", identity=row["id"])["evidence"]["witness"]
    assert witness["target"] == target and witness["stage"] == "geometry"
    assert session.document is before and session.history.cursor == cursor
    session.command("scp.rename", entity=target, name="Renamed")
    session.wait()
    assert session.command("geometry.finding", identity=row["id"])


def test_witness_retains_exact_stage_and_exports_independently(controller, tmp_path):
    target = crossing(controller.session, tmp_path)
    controller.refresh()
    controller.select(target)
    row = finding(controller.session, target)
    controller.spatial_evidence.show(row["id"])
    assert controller.spatial_evidence.lines and controller.spatial_evidence.state["active"]
    frozen = inspection_report.capture(controller.session, target, False)
    inspection_report.capture_finding(controller.session, frozen, row)
    controller.spatial_evidence.clear()
    assert frozen.view["finding"]["evidence"] == row["evidence"]
    controller.spatial_evidence.restore(frozen.view["finding"], frozen=True)
    controller.spatial_evidence.synchronize()
    assert controller.spatial_evidence.state["active"]


def test_surface_eligibility_rejects_grouping_and_curve(session):
    root = session.command("scp.empty", name="Root")
    assert not inspection_surfaces.eligibility(session, root).available
    with pytest.raises(ValueError, match="surface"):
        session.command("geometry.check", target=root)


def test_skin_witness_has_own_stage_and_retains_skin_outputs(controller, tmp_path):
    session = controller.session
    target = crossing(session, tmp_path)
    asset = session.document.entity(target).result.asset
    session.replace_document(skin=replace(session.document.skin, final=SkinStage(asset=asset)))
    before = session.document
    row = finding(session, "skin")
    assert row["target"] == inspection_surfaces.skin_id(before) and row["stage"] == "final"
    controller.spatial_evidence.show(row["id"])
    controller.section_tools.inspect("skin", "final")
    controller.surface_measurements.show("skin", "final")
    controller.surface_measurements.submit()
    session.wait()
    controller.surface_measurements.synchronize()
    assert session.document is before and controller.surface_measurements.report["extents"]
