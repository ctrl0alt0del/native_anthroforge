"""Offscreen Point/Anchor creation, inspector, rebind and picking; no desktop interaction."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

import numpy as np
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.core.points import Anchor
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QGuiApplication.processEvents()


def setup(controller, window):
    controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1.0)
    )
    settle(controller)
    controller.run("workspace.update", dict(cursor=[0, 0, 0.7]))
    click(window, "addConstructionPoint")
    settle(controller)
    assert controller.selectedData["kind"] == "POINT"
    controller.frameSelection()
    assert controller.pick([0, 0, 2], [0, 0, -1], 0, False, 0.04)["id"] == controller.selection
    return controller.selection


def create_anchor(controller, window, point):
    button = find(window, "createOrRebindAnchor")
    assert button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    anchor = controller.session.document.object(controller.selection)
    assert isinstance(anchor, Anchor) and anchor.id != point
    assert not controller.selectedData["transformable"]
    return anchor.id


def rebind(controller, window, anchor):
    controller.run("workspace.update", dict(cursor=[0.3, 0, 0.7]))
    button = find(window, "createOrRebindAnchor")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    np.testing.assert_allclose(
        controller.session.document.object(anchor).resolved_position, [0.3, 0, 0.7], atol=1e-12
    )
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(anchor).resolved_position[0] == 0.0


def capture(window):
    output = Path("build/022-points")
    output.mkdir(parents=True, exist_ok=True)
    QTest.qWait(300)
    assert window.grabWindow().save(str(output / "anchor-inspector.png"))


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(400)
        point = setup(controller, window)
        anchor = create_anchor(controller, window, point)
        rebind(controller, window, anchor)
        capture(window)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run()
            print(
                "Offscreen Point/Anchor creation, explicit rebind, undo and native picking passed."
            )
        finally:
            delete(app)
