"""Exercise editor layout, text-safe shortcuts, search, panels and the empty state."""

import json
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QPoint, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime


def find(window, name):
    pending = [window.contentItem()]
    while pending:
        item = pending.pop()
        if item.objectName() == name:
            return item
        pending.extend(item.childItems())
    result = window.findChild(QObject, name)
    assert result is not None, name
    return result


def click(window, name):
    item = find(window, name)
    point = item.mapToScene(QPointF(item.width() / 2, item.height() / 2))
    QTest.mouseClick(window, Qt.MouseButton.LeftButton, pos=point.toPoint())
    QTest.qWait(80)
    return item


def shortcuts(window):
    click(window, "toolMove")
    QTest.keyClick(window, Qt.Key.Key_E)
    assert window.property("activeTool") == "Rotate"
    search = click(window, "outlinerSearch")
    QTest.keyClick(window, Qt.Key.Key_W)
    assert search.property("text") == "w"
    assert window.property("activeTool") == "Rotate"
    search.setProperty("text", "child")
    QTest.qWait(80)
    assert find(window, "hierarchy").property("count") == 1
    search.setProperty("text", "")
    click(window, "toolMove")


def field_edit(controller, window):
    root = controller.session.document.entities[0].id
    before = controller.session.document.entity(root).matrix
    field = click(window, "transform0")
    QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
    QTest.keyClick(window, Qt.Key.Key_2)
    assert field.property("text") == "2"
    QTest.keyClick(window, Qt.Key.Key_Return)
    QTest.qWait(200)
    assert controller.session.document.entity(root).matrix != before
    QTest.keyClick(window, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
    QTest.qWait(200)
    assert controller.session.document.entity(root).matrix == before


def panel_controls(controller, window):
    root = controller.session.document.entities[0].id
    click(window, "expand_" + root)
    assert find(window, "hierarchy").property("count") == 1
    click(window, "expand_" + root)
    assert find(window, "hierarchy").property("count") == 2
    click(window, "TransformToggle")
    assert not find(window, "transformSection").property("expanded")
    click(window, "TransformToggle")
    viewport = find(window, "viewport")
    viewport.forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_7)
    assert viewport.property("viewName") == "Top" and viewport.property("orthographic")
    QTest.keyClick(window, Qt.Key.Key_5)


def resize_panel(window):
    viewport = find(window, "viewport")
    width = viewport.width()
    edge = viewport.mapToScene(QPointF(-2, viewport.height() / 2)).toPoint()
    QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=edge)
    QTest.mouseMove(window, edge + QPoint(35, 0), 30)
    QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=edge + QPoint(35, 0))
    QTest.qWait(100)
    assert abs(viewport.width() - width) >= 25


def layout_checks(controller, window, output):
    before = controller.session.document.entities[0].matrix
    click(window, "activityToggle")
    assert controller.session.document.entities[0].matrix == before
    assert window.property("activityOpen")
    click(window, "activityToggle")
    window.resize(1050, 680)
    controller.select(controller.session.document.entities[1].id)
    QTest.qWait(200)
    assert find(window, "viewport").width() >= 300
    assert find(window, "inspector").width() >= 260
    assert window.grabWindow().save(str(output / "ui-compact.png"))
    window.resize(1440, 900)
    QTest.qWait(200)
    assert window.grabWindow().save(str(output / "ui-properties.png"))


def verify(controller, window, output):
    shortcuts(window)
    field_edit(controller, window)
    panel_controls(controller, window)
    resize_panel(window)
    layout_checks(controller, window, output)
    controller.replaceDocument("")
    QTest.qWait(300)
    assert not controller.session.document.entities
    assert window.grabWindow().save(str(output / "ui-empty.png"))


def run(project, output):
    controller, warnings = open_controller(project), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, project)
    try:
        QTest.qWait(1000)
        verify(controller, engine.rootObjects()[0], output)
        assert not warnings, warnings
        print(json.dumps({"ui_acceptance": True, "warnings": warnings}))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(sys.argv[1], Path("build").resolve())
