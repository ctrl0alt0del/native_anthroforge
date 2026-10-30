"""Exercise actual QQuickWindow mouse events, rendering, undo and project persistence."""

import json
import sys
from pathlib import Path
from time import monotonic

from PySide6.QtCore import Q_RETURN_ARG, QMetaObject, QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime


def wait_until(predicate, timeout=5):
    deadline = monotonic() + timeout
    while not predicate():
        assert monotonic() < deadline, "Timed out waiting for GUI work"
        QTest.qWait(10)


def health(window):
    raw = QMetaObject.invokeMethod(window, "inspectScene", Q_RETURN_ARG(str))
    value = json.loads(raw)
    assert value["finite"] and value["vertices"] >= 72, value
    return value


def drag(window, point):
    delta = QPoint(65, 0)
    QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=point)
    for step in range(1, 7):
        QTest.mouseMove(window, point + delta * (step / 6), 16)
        QTest.qWait(16)
    QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=point + delta)
    QTest.qWait(100)


def edit_checks(controller, window):
    root = controller.session.document.entities[0].id
    before = controller.session.document.entity(root).matrix
    cursor = controller.session.history.cursor
    scene = health(window)
    assert scene["handle"]
    drag(window, QPoint(*map(round, scene["gizmo"])))
    wait_until(lambda: not controller.session.scheduler.blocked)
    assert controller.session.document.entity(root).matrix != before
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    wait_until(lambda: not controller.session.scheduler.blocked)
    assert controller.session.document.entity(root).matrix == before


def persistence_checks(controller, output):
    target = output / "gui-assembly.anthroforge"
    controller.project_view.saveProject(str(target), "wait")
    wait_until(lambda: controller.session.path == target)
    expected = [e.matrix for e in controller.session.document.entities]
    controller.project_view.replaceDocument(str(target))
    wait_until(lambda: not controller.session.waiting_save, 10)
    assert [e.matrix for e in controller.session.document.entities] == expected
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors


def inspect(controller, window, output, warnings):
    wait_until(lambda: not controller.render_model.pending)
    scene = health(window)
    edit_checks(controller, window)
    persistence_checks(controller, output)
    QTest.qWait(300)
    assert window.grabWindow().save(str(output / "gui-acceptance.png"))
    assert not warnings, warnings
    return {"passed": True, "scene": scene, "mouse_drag_undo": True, "save_reopen": True}


def run(project, output):
    controller, warnings = open_controller(project), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, project)
    try:
        QTest.qWait(1500)
        result = inspect(controller, engine.rootObjects()[0], output, warnings)
        (output / "gui-acceptance.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(sys.argv[1], Path("build").resolve())
