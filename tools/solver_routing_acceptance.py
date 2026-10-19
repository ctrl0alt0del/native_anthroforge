"""Actual routing conversion controls; entirely offscreen, with the user's compact fixture."""

import os
import sys

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find
from ui_polish_acceptance import descendants

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime
from tests.test_routing_surface_pins import scene


def settle(controller):
    controller.session.wait(20)
    controller.refresh()
    QGuiApplication.processEvents()


def click(item):
    assert QMetaObject.invokeMethod(item, "clicked", Qt.DirectConnection)


def select_inputs(window, controller):
    find(window, "curveConversionToggle").setProperty("checked", True)
    find(window, "conversionObstacleToggle").setProperty("checked", True)
    find(window, "conversionEngine").setProperty("currentIndex", 2)
    QGuiApplication.processEvents()
    rows = list(descendants(window.contentItem()))
    for row in rows:
        if row.objectName() in ("conversionPoint", "conversionObstacle"):
            row.setProperty("checked", True)
            click(row)
    assert not find(window, "conversionObstacleNotice").property("visible")
    click(find(window, "previewCurveConversion"))
    settle(controller)
    require_preview(controller)


def require_preview(controller):
    value = controller.session.conversion
    assert value.state == "ready", (value.state, value.error, controller.message)


def exercise(controller, engine):
    root, child, key = scene(controller.session)
    controller.refresh()
    controller.select(key)
    controller.authoring.setEditing(True)
    settle(controller)
    window = engine.rootObjects()[0]
    assert find(window, "routingObstacleNotice").property("visible")
    select_inputs(window, controller)
    click(find(window, "acceptCurveConversion"))
    settle(controller)
    verify_accepted(controller, window, key, {root, child})


def verify_accepted(controller, window, key, targets):
    item = controller.session.document.object(key)
    assert set(item.engine_settings.obstacles) == targets and item.result.status == "ready"
    assert not find(window, "routingObstacleNotice").property("visible")
    capture(window)
    controller.run("undo", {})
    settle(controller)
    assert not controller.session.document.object(key).engine_settings.obstacles


def capture(window):
    target = find(window, "curveConversion")
    parent = target.parentItem()
    while parent.metaObject().indexOfProperty("contentY") < 0:
        parent = parent.parentItem()
    offset = target.mapToItem(parent.property("contentItem"), QPointF(0, 0)).y()
    parent.setProperty("contentY", max(0, offset - 20))
    QTest.qWait(100)
    assert window.grabWindow().save("build/solver-routing/obstacle-editor.png")


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine)
        assert not warnings, warnings
        print("Offscreen obstacle notice, conversion selection, surface contacts and undo passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    Path("build/solver-routing").mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
