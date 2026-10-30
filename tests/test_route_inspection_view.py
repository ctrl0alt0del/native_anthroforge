"""Frozen diagnostic views retain the selected solver step without rerunning routing."""

from anthroforge.application import inspection_report
from tests.test_routing_workflow import create
from tests.test_tissue_interaction import controller as controller


def setup(controller):
    target = create(controller.session)
    controller.refresh()
    controller.selection_view.select(target)
    tool = controller.route_inspection
    tool.start(True)
    controller.session.wait()
    tool.synchronize()
    tool.select(0)
    return target, tool


def test_route_replay_preserves_selected_record_and_never_recalculates(controller):
    target, tool = setup(controller)
    frozen = inspection_report.capture(controller.session, target, False, route=tool.state)
    report = frozen.view["route"]
    tool.hide()
    tool.restore(report)
    jobs = len(controller.session.scheduler.jobs)
    for _ in range(100):
        tool.synchronize()
    assert tool.index == 0 and tool.snapshot()["paths"]
    assert tool.report == report["report"] and len(controller.session.scheduler.jobs) == jobs
    assert "paths" not in tool.state and "contacts" not in tool.state
    controller.selection_view.select("")
    tool.synchronize()
    assert not tool.snapshot()["paths"]


def test_authoring_clears_route_overlay_and_cannot_export_old_evidence(controller):
    target, tool = setup(controller)
    item = controller.session.document.object(target)
    controller.session.command(
        "curve.point.update", curve=target, point=item.points[0].id, position=[-2, 0, 0]
    )
    tool.synchronize()
    assert tool.state["state"] == "stale" and not tool.snapshot()["paths"]
    frozen = inspection_report.capture(controller.session, target, False, route=tool.state)
    assert frozen.view["route"] is None


def test_camera_persistence_preserves_live_route_evidence(controller):
    target, tool = setup(controller)
    controller.viewport_view.saveCamera([0, 0, 0, -35, -25, 0, 2.3], True)
    tool.synchronize()
    assert tool.state["state"] == "ready" and tool.snapshot()["paths"] and tool.index == 0
    frozen = inspection_report.capture(controller.session, target, False, route=tool.state)
    assert frozen.view["route"]["report"]["success"]
