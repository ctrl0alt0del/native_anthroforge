"""Displayed revisions, typed native leases and frozen inspection evidence."""

import pytest

from anthroforge.application import inspection_report
from anthroforge.desktop import tissue_inspection_scene as scene
from tests.test_tissue_interaction import controller as controller
from tests.test_tissue_workflow import assembly


def setup(controller):
    _, _, target = assembly(controller.session)
    controller.refresh()
    controller.select(target)
    publish(controller)
    return target, controller.tissue_inspection


def publish(controller):
    for _ in range(8):
        controller.process_tick()
        controller.frame_presented()


def test_switching_buffer_types_retains_old_render_contract_until_frame_boundary(controller):
    _, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    publish(controller)
    old = scene.primary(tool)
    tool.set_view("rest", "base", "Displacement")
    controller.session.wait()
    tool.synchronize()
    retained = scene.primary(tool)
    assert retained["kind"] == "MESH" and retained["handle"] == old["handle"]
    publish(controller)
    current = scene.primary(tool)
    assert current["kind"] == "HEAT" and current["mesh_handle"] == old["handle"]
    assert scene.mesh(tool, dict(current, handle=current["mesh_handle"])) is not None


def test_stage_inspection_picking_and_cancel_do_not_edit_anatomy(controller):
    target, tool = setup(controller)
    before, history = controller.session.document, controller.session.history.cursor
    tool.set_view("rest", "", "Overlay")
    publish(controller)
    row = controller.pick_rows[target]
    assert row["geometry_asset"] == before.object(target).rest_result.asset
    tool.arm()
    tool.pick([0.5, 0.2, 5], [0, 0, -1])
    controller.session.wait()
    tool.synchronize()
    assert tool.point and tool.lines
    tool.cancel()
    assert controller.session.document is before and controller.session.history.cursor == history


def test_export_freezes_stage_settings_without_reusing_live_ui_state(controller):
    target, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    options = controller.inspection_export.options("build/inspect.afinspection.zip")
    frozen = inspection_report.capture(controller.session, target, False, options["tissue"])
    tool.set_view("intrinsic", "", "Overlay")
    assert frozen.view["tissue"]["stage"] == "rest"
    assert frozen.view["tissue"]["reference"] == "base"
    assert frozen.source.document is controller.session.document


def test_component_edit_protects_inspection_navigation(controller):
    _, tool = setup(controller)
    controller.session.begin()
    with pytest.raises(ValueError, match="Finish"):
        tool.arm()
    controller.session.cancel()


def test_idle_inspection_does_not_repeat_native_stage_preparation(controller, monkeypatch):
    _, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    publish(controller)
    calls = []
    original = tool.refresh_projection
    monkeypatch.setattr(tool, "refresh_projection", lambda: (calls.append(1), original()))
    for _ in range(100):
        tool.synchronize()
        assert tool.state["stage"] == "rest"
    assert not calls


def test_changing_stage_clears_points_from_the_previous_surface(controller):
    _, tool = setup(controller)
    tool.set_view("rest", "", "Overlay")
    publish(controller)
    tool.pick([0.5, 0.2, 5], [0, 0, -1])
    controller.session.wait()
    tool.synchronize()
    assert tool.point
    tool.set_view("base", "", "Overlay")
    publish(controller)
    assert not tool.point and not tool.lines


def test_visibility_reads_use_prepared_properties_without_rebuilding_reports(
    controller, monkeypatch
):
    target, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    publish(controller)
    projection = tool.state
    monkeypatch.setattr(tool, "state_values", lambda: pytest.fail("Rebuilt a report on read"))
    for _ in range(1000):
        assert tool.state is projection
        assert projection.value("hiddenOwners") == [target]
    assert tool.snapshot()["stages"] and tool.snapshot()["hiddenOwners"] == [target]


def test_selection_clear_discards_prepared_inspection_state(controller):
    _, tool = setup(controller)
    tool.set_view("rest", "base", "Overlay")
    publish(controller)
    controller.select("")
    publish(controller)
    state = tool.snapshot()
    assert state["target"] == "" and state["stages"] == [] and state["hiddenOwners"] == []
