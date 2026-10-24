"""Mirrored presentation is instance-aware without authored tree entries."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.core.mirroring import MirrorInstance
from anthroforge.desktop.controller import Controller
from tests.conftest import CUBE


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    yield value
    value.close()
    assert app


def mirrored_cube(controller):
    session = controller.session
    root = session.command("scp.empty", name="Skeleton")
    child = session.command("import", path=str(CUBE), units=1.0, parent=root)["entity_id"]
    session.command("wait")
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    controller.refresh()
    return root, child, MirrorInstance(child, root).id


def test_viewport_mirror_is_selectable_but_absent_from_both_trees(controller):
    root, child, instance = mirrored_cube(controller)
    assert instance not in controller.scene_projection.records
    assert instance not in controller.construction.records
    rows = {r["id"]: r for r in controller._render_rows}
    assert rows[instance]["handle"] == rows[child]["handle"]
    controller.select(instance)
    assert controller.selection == instance
    assert controller.selectedData.get("readonly")
    assert controller.selectedData.get("mirror_source") == child
    assert not controller.selectedData.get("transformable")
    assert not controller.mirror_records[instance]["context_dimmed"]
    controller.select(child)
    assert not controller.selectedData.get("readonly")


def test_display_mode_preserves_computation_and_instance_identity(controller):
    root, child, instance = mirrored_cube(controller)
    source = controller.session.document.entity(child)
    controller.session.command("workspace.update", mirror_display="SOURCE")
    controller.refresh()
    rows = {r["id"]: r for r in controller._render_rows}
    assert not rows[instance]["surface_visible"]
    controller.session.command("workspace.update", mirror_display="MIRROR")
    controller.refresh()
    rows = {r["id"]: r for r in controller._render_rows}
    assert rows[instance]["surface_visible"] and not rows[child]["surface_visible"]
    assert controller.session.document.entity(child) is source


def test_hiding_source_does_not_hide_its_mirror_and_projection_is_reused(controller):
    root, child, instance = mirrored_cube(controller)
    controller.refresh()
    first = controller.mirror_records[instance]
    controller.refresh()
    assert controller.mirror_records[instance] is first
    controller.session.command("workspace.update", hidden=[child])
    controller.refresh()
    rows = {r["id"]: r for r in controller._render_rows}
    assert rows[instance]["surface_visible"]
    assert not rows[child]["surface_visible"]


def test_focusing_mirror_uses_the_shared_source_scope_and_keeps_readonly_selection(controller):
    root, child, instance = mirrored_cube(controller)
    controller.select(instance)
    controller.focusSelection()
    assert controller.session.workspace.members == (child,)
    assert controller.selection == instance
    assert controller.selectedData.get("readonly")
    assert not controller.selectedData.get("context_dimmed")
