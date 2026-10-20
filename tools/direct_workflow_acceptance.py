"""Actual QML direct workflows, synthetic documents and no desktop input."""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtTest import QTest
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    scene,
    settle,
)
from ui_acceptance import click as mouse_click
from ui_acceptance import find
from ui_polish_acceptance import descendants

from tests.test_fiber_creation import CUBE
from tests.test_reference_images import source as image_source

OUTPUT = Path("build/ui-direct-workflows")


def visible(window, name):
    choices = [item for item in descendants(window.contentItem()) if item.objectName() == name]
    return next(item for item in choices if item.isVisible())


def click(item):
    assert item.isEnabled()
    assert QMetaObject.invokeMethod(item, "clicked", Qt.DirectConnection)


def snapshot(window, name):
    QTest.qWait(80)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def curve_scene(controller):
    bone = controller.run("import", dict(path=str(CUBE), units=1.0))["entity_id"]
    points = [dict(position=[i * 0.005, 0, 0.6]) for i in range(120)]
    curve = controller.run("curve.create", dict(points=points, engine="POLYLINE"))
    settle(controller)
    controller.select(curve)
    controller.authoring.setEditing(False)
    settle(controller)
    return bone, curve


def fiber(controller, window):
    bone, source = curve_scene(controller)
    before = len(controller.session.history.entries)
    click(visible(window, "createFiberFromCurve"))
    settle(controller)
    selected = controller.session.document.object(controller.selection)
    assert selected.id != source and selected.bindings
    assert {b.target for b in selected.bindings} == {bone}
    assert not controller.authoring.editing
    assert len(controller.session.history.entries) == before + 1
    controller.run("undo", {})
    settle(controller)
    controller.select(source)
    dense_fiber_options(controller, window)


def dense_fiber_options(controller, window):
    click(visible(window, "Fiber binding optionsToggle"))
    settle(controller)
    view = visible(window, "fiberBindingList")
    assert view.property("count") == 2
    all_points = visible(window, "fiberAllPoints")
    all_points.setProperty("checked", True)
    settle(controller)
    assert view.property("count") == 120
    assert len(view.property("contentItem").childItems()) < 15
    view.setProperty("contentY", view.property("contentHeight") - view.height())
    settle(controller)
    assert len(view.property("contentItem").childItems()) < 15
    snapshot(window, "fiber-options")


def empty_tissue_picker(window):
    mouse_click(window, "createTissueToolbar")
    assert find(window, "tissueCreationDialog").property("visible")
    QMetaObject.invokeMethod(find(window, "tissueCreationDialog"), "close", Qt.DirectConnection)


def tissue_and_source(controller, window):
    empty_tissue_picker(window)
    scene(controller)
    membrane = controller.selection
    mouse_click(window, "createTissueToolbar")
    settle(controller)
    assert controller.selectedData["is_tissue"] and not controller.authoring.editing
    click(visible(window, "editTissueSource"))
    settle(controller)
    assert controller.selection == membrane
    click(visible(window, "editSurfaceSource"))
    settle(controller)
    assert controller.selectedData["kind"] == "FIBER" and controller.authoring.editing
    snapshot(window, "edit-source")


def tissue_picker(controller, window):
    scene(controller)
    membrane = controller.selection
    controller.select("")
    mouse_click(window, "createTissueToolbar")
    dialog = find(window, "tissueCreationDialog")
    assert dialog.property("visible")
    dialog.setProperty("source", membrane)
    settle(controller)
    click(find(window, "createChosenTissue"))
    settle(controller)
    assert controller.session.document.object(controller.selection).source == membrane
    assert not dialog.property("visible")


def trace_image(controller, window):
    result = controller.run("image.import", dict(path=image_source(OUTPUT), width=2))
    settle(controller)
    controller.select(result["object_id"])
    settle(controller)
    before = controller.session.history.cursor
    click(visible(window, "traceImage"))
    tool = controller.drawing_tools
    assert tool.mode == "DRAW" and tool.options["image"] == result["object_id"]
    assert tool.options["depth"] == "IMAGE"
    for x in (-0.3, -0.1, 0.1, 0.3):
        tool.pointer([x, x * x, 2, 0, 0, -1, x * 100, x * x * 100, 1], [0, 0, 1], x == -0.3)
    tool.release()
    settle(controller)
    verify_traced(controller, before, result["object_id"])


def verify_traced(controller, before, image):
    from anthroforge.core.construction import Curve

    curves = [o for o in controller.session.document.objects if isinstance(o, Curve)]
    assert len(curves) == 1, controller.message
    assert all(abs(p.position[2]) < 1e-8 for p in curves[0].points)
    assert not curves[0].parent and image not in curves[0].owners
    assert controller.session.history.cursor == before + 1
    controller.drawing_tools.cancel()
    controller.run("undo", {})
    assert curves[0].id not in controller.session.document.registry.records


def members(controller, window):
    bone, _ = curve_scene(controller)
    controller.select(bone)
    controller.authoring.setEditing(True)
    controller.authoring.selectComponent(controller.authoring.componentRows[0]["key"], False)
    controller.authoring.addDeformer("HOOK")
    settle(controller)
    controller.select(bone)
    controller.authoring.setEditing(False)
    settle(controller)
    buttons = [
        r for r in descendants(window.contentItem()) if r.property("text") == "Select members"
    ]
    click(next(item for item in buttons if item.isVisible()))
    assert controller.authoring.editing and len(controller.authoring.selection) == 1


def request_delete(window, target):
    assert QMetaObject.invokeMethod(
        find(window, "deleteDialog"), "request", Qt.DirectConnection, Q_ARG("QVariant", target)
    )


def deletion(controller, window):
    parent = controller.run("scp.empty", dict(name="Root"))
    child = controller.run("scp.empty", dict(name="Child", parent=parent))
    settle(controller)
    controller.select(child)
    request_delete(window, child)
    assert child not in controller.session.document.registry.records
    assert not find(window, "deleteDialog").property("visible")
    controller.run("undo", {})
    settle(controller)
    request_delete(window, parent)
    assert find(window, "deleteDialog").property("visible")
    assert parent in controller.session.document.registry.records
    QMetaObject.invokeMethod(find(window, "deleteDialog"), "reject", Qt.DirectConnection)


def focus_workspace(controller, window):
    parent = controller.run("scp.empty", dict(name="Root"))
    child = controller.run("scp.empty", dict(name="Child", parent=parent))
    settle(controller)
    controller.select(parent)
    click(find(window, "focusSelection"))
    assert set(controller.session.workspace.members) == {parent, child}
    assert controller.session.workspace.name == "Root"
    assert not window.property("modalOpen")
    click(find(window, "manageWorkspace"))
    assert not window.property("modalOpen")
    rename_workspace(controller, window)


def rename_workspace(controller, window):
    field = find(window, "workspaceName")
    field.forceActiveFocus()
    field.setProperty("text", "Inspection")
    QMetaObject.invokeMethod(field, "editingFinished", Qt.DirectConnection)
    assert controller.session.workspace.name == "Inspection"
    settle(controller)
    assert (
        find(window, "workspaceSelector").property("currentIndex")
        == controller.session.active_workspace
    )
    navigate_workspace(window)


def navigate_workspace(window):
    viewport = find(window, "viewport")
    viewport.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_3)
    assert viewport.property("viewName") == "Top"
    snapshot(window, "workspace")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            for scenario in SCENARIOS:
                run(scenario)
                print(scenario.__name__ + ": passed", flush=True)
        finally:
            delete(app)


SCENARIOS = (
    fiber,
    tissue_and_source,
    tissue_picker,
    trace_image,
    members,
    deletion,
    focus_workspace,
)


if __name__ == "__main__":
    main()
