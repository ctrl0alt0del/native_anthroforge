"""Background-only QML toolbar and surface-click Fiber authoring acceptance."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.core.fibers import Fiber
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(5)
    controller.refresh()
    for _ in range(8):
        controller.render_model.drain()
        controller.path_model.drain()
        controller.frame_presented()


def exercise(controller, engine):
    root = engine.rootObjects()[0]
    source = Path("examples/primitives/cube.obj").resolve()
    controller.run("import", dict(path=str(source), units=1.0))
    settle(controller)
    button = find(root, "placeFiberPoints")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    tool = controller.drawing_tools
    assert tool.mode == "FIBER"
    before = controller.session.history.cursor
    for x, continuing in ((-0.4, False), (0, True), (0.4, False)):
        tool.click([x, 0, 3, 0, 0, -1, 400 + x * 100, 300, 1], [0, 0, -1], continuing)
    qualify(controller, before)


def qualify(controller, before):
    settle(controller)
    fiber = controller.session.document.object(controller.selection)
    assert isinstance(fiber, Fiber) and fiber.engine == "ROUTED"
    assert len(fiber.bindings) == 3 and controller.session.history.cursor == before + 1
    assert len(controller.session.document.objects) == 1
    assert not controller.drawing_tools.mode
    controller.run("undo", {})
    assert not controller.session.document.objects
    controller.run("redo", {})
    settle(controller)
    assert controller.session.document.object(fiber.id).result.asset


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        exercise(controller, engine)
        assert not controller.message, controller.message
        assert not warnings, warnings
        print("Offscreen quick Fiber: toolbar, clicked pins, routing, selection and undo passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
