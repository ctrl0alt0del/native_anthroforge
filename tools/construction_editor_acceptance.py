"""Offscreen QML/controller acceptance; never creates a visible desktop window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(5)
    controller.refresh()


def setup(controller):
    key = controller.run("curve.create", {})
    settle(controller)
    controller.select(key)
    controller.authoring.setEditing(True)
    controller.inspection_panel.activate(True)
    controller.frameSelection()
    assert not controller.session.document.entities
    assert controller.constructionModel.rowCount() == 1
    assert controller.authoring.componentRows and controller.authoring.lines
    return key


def component_drag(controller, key):
    editor = controller.authoring
    row = next(r for r in editor.componentRows if r["part"] == "position")
    editor.selectComponent(row["key"], False)
    before = controller.session.history.cursor
    assert controller.beginTransform("Move")
    controller.transformDelta([0, 0.2, 0, 0, 0, 0, 1, 1, 1])
    controller.endTransform(False)
    settle(controller)
    actual = controller.session.document.object(key).points[0].position
    np.testing.assert_allclose(actual, np.array(row["world"]) + [0, 0.2, 0])
    assert controller.session.history.cursor == before + 1
    undo_drag(controller, key, row["world"])


def undo_drag(controller, key, expected):
    controller.run("undo", {})
    np.testing.assert_allclose(controller.session.document.object(key).points[0].position, expected)


def insertion(controller, key):
    settle(controller)
    interaction = controller.authoring.interaction
    interaction.updatePreview([0, 0, 2], [0, 0, -1])
    assert interaction.preview and interaction.insert()
    assert len(controller.session.document.object(key).points) == 3
    assert controller.authoring.selectedComponent["point"]
    controller.authoring.setEditing(False)
    assert controller.beginTransform("Move")
    controller.transformDelta([0, 0, 0.3, 0, 0, 0, 1, 1, 1])
    controller.endTransform(True)
    assert controller.session.document.object(key).matrix[11] == 0


def image_inspector(controller):
    path = Path("build/020-image-scene/inspector.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 4), "blue").save(path)
    result = controller.run("image.import", dict(path=str(path)))
    settle(controller)
    controller.select(result["object_id"])
    assert controller.selectedData["kind"] == "IMAGE"
    assert controller.ordinaryParents()
    assert controller.beginTransform("Move")
    controller.transformDelta([0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    controller.endTransform(True)
    controller.frameSelection()


def shared_sources(controller):
    keys = [controller.run("curve.create", {}) for _ in range(2)]
    controller.select(keys[1])
    controller.select(keys[0], True)
    assert controller.selectedObjects == keys[::-1]
    controller.authoring.create("LOFT", "CAPSULE")
    settle(controller)
    item = controller.session.document.entity(controller.selection)
    assert [u.curve for u in item.primitive.curves] == keys[::-1]
    assert controller.authoring.state.get("uses")[0]["users"][0]["id"] == item.id
    assert item.result.status == "ready"
    selection_removal(controller, item.id, keys)


def selection_removal(controller, consumer, keys):
    controller.run("scp.delete", dict(entity=consumer))
    controller.select(keys[0])
    controller.select(keys[1], True)
    controller.run("object.delete", dict(target=keys[1]))
    assert controller.selectedObjects == [keys[0]]
    controller.run("undo", {})
    controller.select(keys[1], True)
    controller.select(keys[0], True)
    assert controller.selectedObjects == [keys[1]]


def interactions(controller):
    key = setup(controller)
    component_drag(controller, key)
    insertion(controller, key)
    image_inspector(controller)
    shared_sources(controller)
    drawing_gestures(controller)
    conversion_preview(controller)


def control_navigation(controller, engine):
    curve = controller.run("curve.create", {})
    control = controller.run("control.create", dict(entity=curve))
    settle(controller)
    controller.select(control)
    assert control in controller.construction.records
    assert all(row["id"] != control for row in controller.treeRows)
    assert controller.selectedData["is_control"]
    assert controller.authoring.state["follow"] == curve
    parent = find(engine.rootObjects()[0], "controlParent")
    assert parent.property("currentValue") == curve
    controller.run("object.transform", dict(target=curve, values=[0.4, 0, 0, 0, 0, 0, 1, 1, 1]))
    settle(controller)
    assert controller.selectedData["trs"][0] == 0.4


def conversion_preview(controller):
    key = controller.run("curve.create", {})
    settle(controller)
    controller.select(key)
    result = controller.run("curve.conversion.preview", dict(curve=key, engine="POLYLINE"))
    settle(controller)
    assert controller.conversionState["state"] == "ready"
    rows = [row for row in controller.path_model.wanted.values() if row.get("preview")]
    assert rows and all(not row["pickable"] for row in rows)
    controller.run("curve.conversion.accept", dict(token=result["token"]))
    settle(controller)
    assert controller.session.document.object(key).engine == "POLYLINE"
    assert not any(row.get("preview") for row in controller.path_model.rows)


def stroke_pointer(x, y=0):
    return [x, y, 3, 0, 0, -1, 100 + x * 100, 100 + y * 100, 1]


def drawing_gestures(controller):
    tool = controller.drawing_tools
    controller.run("workspace.update", dict(cursor=[0, 0, 0.4]))
    tool.begin("POINTS")
    before = controller.session.history.cursor
    tool.pointer(stroke_pointer(0), [0, 0, -1], True)
    tool.pointer(stroke_pointer(0.4), [0, 0, -1], True)
    tool.removeLast()
    assert tool.stroke.count == 1
    tool.pointer(stroke_pointer(0.5), [0, 0, -1], True)
    tool.finish()
    settle(controller)
    assert controller.session.history.cursor == before + 1 and not tool.mode
    repeated_draws(controller)


def repeated_draws(controller):
    tool = controller.drawing_tools
    tool.begin("DRAW")
    before = controller.session.history.cursor
    for y in (0.2, 0.4):
        tool.pointer(stroke_pointer(0, y), [0, 0, -1], True)
        tool.pointer(stroke_pointer(0.3, y), [0, 0, -1], False)
        tool.release()
    settle(controller)
    assert controller.session.history.cursor == before + 2 and tool.mode == "DRAW"
    tool.pointer(stroke_pointer(0), [0, 0, -1], True)
    tool.cancel()
    assert controller.session.history.cursor == before + 2 and tool.stroke is None


def image_axis_control(controller, engine):
    target = next(
        row["id"] for row in controller.construction.records.values() if row["kind"] == "IMAGE"
    )
    controller.select(target)
    settle(controller)
    checkbox = find(engine.rootObjects()[0], "imageAxisVisibility")
    checkbox.setProperty("checked", True)
    assert QMetaObject.invokeMethod(checkbox, "clicked", Qt.DirectConnection)
    assert controller.session.workspace.reference_images[-1].only_axis_aligned


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        interactions(controller)
        control_navigation(controller, engine)
        image_axis_control(controller, engine)
        assert not controller.message, controller.message
        assert not warnings, warnings
        print("Offscreen construction editor: curves, images and ordered source selection passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
