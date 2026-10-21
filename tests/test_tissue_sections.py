"""Read-only section jobs share stage provenance and presentation-only plane settings."""

from anthroforge.application import inspection_report
from tests.test_tissue_inspection_view import publish, setup
from tests.test_tissue_interaction import controller as controller


def section(controller):
    target, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    publish(controller)
    view = controller.section_tools
    view.enable(True)
    publish(controller)
    view.timer.stop()
    view.submit()
    controller.session.wait()
    publish(controller)
    return target, view


def test_section_contours_compare_same_plane_without_editing_document(controller):
    target, tool = section(controller)
    before, cursor = controller.session.document, controller.session.history.cursor
    assert {r["stage"] for r in tool.reports} == {"rest", "base"}
    assert all(r["owner"] == target and r["lines"] for r in tool.reports)
    tool.setting("position", tool.position + 0.1)
    assert not tool.reports
    tool.timer.stop()
    tool.submit()
    controller.session.wait()
    publish(controller)
    assert controller.session.document is before and controller.session.history.cursor == cursor


def test_section_scope_and_pick_mask_rebuild_on_plane_change(controller):
    target, tool = section(controller)
    owners = [target, "context"]
    first = tool.planes(owners)
    assert first[0] == tool.plane and first[1] == [0, 0, 0, 0]
    assert tool.planes(owners) is first
    tool.setting("whole_scene", True)
    second = tool.planes(owners)
    assert second is not first and second[0] == second[1]
    tool.cancel()
    assert not tool.applies(target) and not tool.reports


def test_section_export_retains_settings_and_accepted_contour_evidence(controller):
    target, tool = section(controller)
    options = controller.inspection_export.options("build/section.afinspection.zip")
    snapshot = inspection_report.capture(controller.session, target, False, options["tissue"])
    evidence = snapshot.view["tissue"]["section"]
    assert evidence["settings"]["position"] == tool.position
    assert evidence["report"]["surfaces"] == tool.reports
    tool.cancel()
    assert evidence["settings"]["enabled"]


def test_camera_save_retains_contours_without_rescheduling(controller):
    _, tool = section(controller)
    before = tool.reports
    jobs = len(controller.session.scheduler.jobs)
    controller.saveCamera([0, 0, 0, -35, -25, 0, 2.3], True)
    publish(controller)
    assert tool.reports == before and not tool.timer.isActive()
    assert len(controller.session.scheduler.jobs) == jobs
