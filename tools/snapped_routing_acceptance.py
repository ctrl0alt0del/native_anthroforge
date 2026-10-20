"""Offscreen active/target/preview engine states on the user's saved Curve and Fiber."""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.application import projects, storage
from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime
from anthroforge.native import path_collisions


def settle(controller):
    controller.session.wait(30)
    controller.refresh()
    QGuiApplication.processEvents()


def click(window, name):
    assert QMetaObject.invokeMethod(find(window, name), "clicked", Qt.DirectConnection)


def select(controller, window, key, expected):
    controller.select(key)
    controller.authoring.setEditing(True)
    settle(controller)
    assert find(window, "conversionEngine").property("currentText") == expected, (
        expected,
        find(window, "conversionEngine").property("currentText"),
        controller.session.document.object(key).engine,
        find(window, "curveConversion").property("sourceEngine"),
    )
    assert find(window, "activeCurveEngine").property("text") == "Active engine · " + expected


def target(controller, window, key):
    select(controller, window, key, "BEZIER")
    before = controller.session.document
    find(window, "curveConversionToggle").setProperty("checked", True)
    find(window, "conversionEngine").setProperty("currentIndex", 2)
    QGuiApplication.processEvents()
    assert controller.session.document is before
    assert "ROUTED is not active" in find(window, "conversionEngineStatus").property("text")
    click(window, "previewCurveConversion")
    settle(controller)
    assert controller.session.conversion.state == "ready", controller.session.conversion.error
    assert controller.session.document.object(key).engine == "BEZIER"
    assert "not applied" in find(window, "conversionPreviewStatus").property("text")
    assert find(window, "acceptCurveConversion").property("text") == "Use ROUTED"


def accept(controller, window, key):
    click(window, "acceptCurveConversion")
    settle(controller)
    assert controller.session.document.object(key).engine == "ROUTED"
    assert find(window, "activeCurveEngine").property("text") == "Active engine · ROUTED"
    verify_path(controller, key)


def verify_path(controller, key):
    session = controller.session
    curve, cube = session.document.object(key), session.document.entities[0]
    assert curve.result.status == "ready", curve.result.error
    path = session.resources.paths[curve.result.asset].path
    mesh = session.resources.meshes[cube.result.asset].mesh
    row = path_collisions.row(path, curve.matrix, (1,) * len(curve.points))
    collisions, _ = path_collisions.check(session.engine, [row], [mesh.handle], [cube.matrix])
    assert (collisions < 0).all(), collisions


def capture(window, output):
    target = find(window, "curveConversion")
    parent = target.parentItem()
    while parent.metaObject().indexOfProperty("contentY") < 0:
        parent = parent.parentItem()
    offset = target.mapToItem(parent.property("contentItem"), QPointF(0, 0)).y()
    parent.setProperty("contentY", max(0, offset - 20))
    QTest.qWait(100)
    assert window.grabWindow().save(str(output))


def history(controller, window, key):
    controller.run("undo", {})
    settle(controller)
    select(controller, window, key, "BEZIER")
    controller.run("redo", {})
    settle(controller)
    select(controller, window, key, "ROUTED")
    verify_path(controller, key)


def exercise(controller, window, output):
    objects = controller.session.document.objects
    curve = next(item for item in objects if type(item) is Curve)
    fiber = next(item for item in objects if isinstance(item, Fiber))
    target(controller, window, curve.id)
    capture(window, output / "conversion-preview.png")
    accept(controller, window, curve.id)
    history(controller, window, curve.id)
    target(controller, window, fiber.id)
    accept(controller, window, fiber.id)
    select(controller, window, curve.id, "ROUTED")
    capture(window, output / "conversion-applied.png")
    cancel_preview(controller, curve.id)


def cancel_preview(controller, key):
    controller.run("curve.conversion.preview", dict(curve=key, engine="POLYLINE"))
    settle(controller)
    controller.run("curve.conversion.cancel", {})
    assert controller.session.document.object(key).engine == "ROUTED"


def run(project, output):
    controller, warnings = Controller(), []
    projects.adopt(controller.session, *storage.read_package(project, controller.session.engine))
    controller.refresh()
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine.rootObjects()[0], output)
        assert not warnings, warnings
        print("Saved Curve/Fiber conversion, unchanged previews, engine states and undo passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    output = Path("build/snapped-solver-routing")
    output.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(Path(sys.argv[1]), output)
