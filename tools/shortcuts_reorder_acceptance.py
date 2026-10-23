"""Production shortcut list drag/cancel/undo through offscreen Qt mouse events."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QUICK_BACKEND"] = "software"

from pathlib import Path

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shortcuts_editor_acceptance import create_engine, prepare, settle
from ui_acceptance import find

from anthroforge.desktop.controller import Controller


def point(window, key):
    handle = find(window, "reorderShortcut" + key)
    return handle.mapToScene(QPointF(handle.width() / 2, handle.height() / 2)).toPoint()


def drag(window, source, target, cancel=False):
    start, end = point(window, source), point(window, target)
    end.setY(end.y() + 28)
    QTest.mousePress(window, Qt.LeftButton, pos=start)
    for step in range(1, 9):
        QTest.mouseMove(window, start + (end - start) * (step / 8), 12)
    if cancel:
        QTest.keyClick(window, Qt.Key_Escape)
        QTest.mouseMove(window, end + QPointF(0, 16).toPoint(), 20)
    QTest.mouseRelease(window, Qt.LeftButton, pos=end)
    QTest.qWait(80)


def order(controller):
    return [row["key"] for row in controller.shortcut_panel.model.rows]


def exercise(controller, window, first, others):
    panel = controller.shortcut_panel
    panel.editor.select("")
    settle(controller)
    before, cursor = order(controller), controller.session.history.cursor
    drag(window, first, others[1])
    assert order(controller) == [others[0], others[1], first, others[2]]
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    assert order(controller) == before
    cursor = controller.session.history.cursor
    drag(window, first, others[1], cancel=True)
    assert order(controller) == before and controller.session.history.cursor == cursor


def run():
    controller, warnings = Controller(), []
    try:
        curve, first, _ = prepare(controller)
        others = [
            controller.run("driver.create", dict(label="Control " + str(i))) for i in range(3)
        ]
        engine = create_engine(controller, curve, warnings)
        window = engine.rootObjects()[0]
        exercise(controller, window, first, others)
        capture(window)
        assert not warnings, warnings
        window.close()
    finally:
        controller.close()


def capture(window):
    output = Path("build/shortcuts-editor-review/reorder.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    assert window.grabWindow().save(str(output))


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    run()
    print("Shortcut drag reordering, one-action undo and Escape cancellation passed.")
