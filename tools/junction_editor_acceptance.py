"""Invoke actual junction controls in the full QML editor without a visible window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from fiber_editor_acceptance import settle
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def click(controller, window, name):
    button = find(window, name)
    assert button.property("enabled"), name
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)


def setup(controller):
    a = controller.run("curve.create", dict(name="Source"))
    b = controller.run("curve.create", dict(name="Follower"))
    settle(controller)
    controller.select(a)
    controller.authoring.setEditing(True)
    settle(controller)
    return a, b


def controls(controller, window):
    a, b = setup(controller)
    click(controller, window, "Shared junctionToggle")
    click(controller, window, "createJunction")
    assert len(controller.session.document.junctions) == 1, controller.message
    point = controller.session.document.object(a).points[0].id
    info = controller.authoring.junctionOptions(a, point)
    assert set(info["members"]) == {"Source", "Follower"}
    click(controller, window, "removeJunction")
    assert not controller.session.document.junctions, controller.message
    controller.run("undo", {})
    settle(controller)
    assert len(controller.session.document.junctions) == 1
    assert controller.authoring.editing and controller.selection == a


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        window.hide()
        controls(controller, window)
        assert not warnings, warnings
        print("Offscreen junction join, detach and undo controls passed without QML warnings.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
