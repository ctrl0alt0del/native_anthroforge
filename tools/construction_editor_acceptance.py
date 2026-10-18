"""Offscreen QML/controller acceptance; never creates a visible desktop window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import numpy as np
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete

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


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        key = setup(controller)
        component_drag(controller, key)
        insertion(controller, key)
        assert not controller.message, controller.message
        assert not warnings, warnings
        print("Offscreen curve editor: selection, inspection, drag/undo, insertion, cancel passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
