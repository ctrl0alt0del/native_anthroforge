"""Actual QML pointer strokes and controls using Qt's offscreen platform only."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

from curve_interaction_acceptance import screen
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from tissue_editor_acceptance import run, settle
from tissue_scene_acceptance import scene
from ui_acceptance import find

from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/vcp-visual-tools")
LEFT = Qt.MouseButton.LeftButton


def paint(controller, window):
    target = scene(controller)
    controller.run("tissue.field.create", dict(target=target, name="paint", domain="REST"))
    settle(controller)
    controller.tissue_painting.begin("paint")
    controller.cameraRequested.emit([0, 0, 0.65, -90, 0, 0, 1.4], True)
    QTest.qWait(300)
    before = controller.session.document
    stroke(controller, window)
    assert any(controller.session.document.object(target).fields[0].values)
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(target).fields == before.object(target).fields
    cancel_stroke(controller, window)
    return target


def stroke(controller, window):
    cursor = controller.session.history.cursor
    start, end = screen(window, [-0.1, 0, 0.7]), screen(window, [0.1, 0, 0.7])
    QTest.mouseMove(window, start)
    QTest.mousePress(window, LEFT, pos=start)
    QTest.mouseMove(window, end, delay=80)
    QTest.qWait(200)
    assert controller.tissue_painting.dragging
    assert window.grabWindow().save(str(OUTPUT / "painting-ui.png"))
    QTest.mouseRelease(window, LEFT, pos=end)
    settle(controller)
    QTest.qWait(200)
    assert controller.session.history.cursor == cursor + 1


def cancel_stroke(controller, window):
    before = controller.session.document
    point = screen(window, [0, 0, 0.7])
    QTest.mousePress(window, LEFT, pos=point)
    QTest.qWait(80)
    QTest.keyClick(window, Qt.Key.Key_Escape)
    QTest.mouseRelease(window, LEFT, pos=point)
    settle(controller)
    assert controller.session.document is before and not controller.tissue_painting.name


def section(controller, window):
    checkbox = find(window, "sectionEnabled")
    checkbox.setProperty("checked", True)
    assert QMetaObject.invokeMethod(checkbox, "toggled", Qt.DirectConnection)
    QTest.qWait(250)
    settle(controller)
    assert controller.section_tools.enabled and controller.section_tools.reports, (
        controller.section_tools.state
    )
    controller.section_tools.setting("position", 0.1)
    QTest.qWait(150)
    settle(controller)
    assert window.grabWindow().save(str(OUTPUT / "sections-ui.png"))


def route(controller, window):
    key = controller.run(
        "curve.create",
        dict(engine="ROUTED", points=[dict(position=[-0.8, 0, 0]), dict(position=[0.8, 0, 0])]),
    )
    settle(controller)
    controller.select(key)
    controller.authoring.setEditing(True)
    QTest.qWait(150)
    button = find(window, "inspectRoute")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    tool = controller.route_inspection
    assert tool.report.get("success") and tool.paths, tool.state
    assert window.grabWindow().save(str(OUTPUT / "route-ui.png"))


def exercise(controller, window):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    window.resize(1440, 950)
    paint(controller, window)
    section(controller, window)
    route(controller, window)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(exercise)
        finally:
            delete(app)
    print("Offscreen QML brush commit/cancel/undo, section and route controls passed.")
