"""Direct engine selection and one-action undo on the user's saved Curve and Fiber."""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if sys.platform == "win32":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from PySide6.QtCore import Q_ARG, QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find
from ui_polish_acceptance import descendants

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


def choose(window, index, name="standaloneEngineChoice"):
    control = selector(window, name)
    assert control.property("visible") and control.property("enabled")
    control.setProperty("currentIndex", index)
    assert QMetaObject.invokeMethod(control, "activated", Qt.DirectConnection, Q_ARG(int, index))


def selector(window, name):
    return next(
        item
        for item in descendants(window.contentItem())
        if item.objectName() == name and item.property("visible")
    )


def select(controller, window, key, expected):
    controller.selection_view.select(key)
    settle(controller)
    assert find(window, "standaloneEngineChoice").property("currentText") == expected, (
        expected,
        find(window, "standaloneEngineChoice").property("currentText"),
        controller.session.document.object(key).engine,
    )


def target(controller, window, key):
    select(controller, window, key, "BEZIER")
    before, cursor = controller.session.document.object(key), controller.session.history.cursor
    choose(window, 2)
    assert controller.session.document.object(key).engine == "ROUTED"
    settle(controller)
    assert controller.session.history.cursor == cursor + 1
    assert [p.id for p in controller.session.document.object(key).points] == [
        p.id for p in before.points
    ]
    assert controller.session.conversion.state == "idle"
    assert find(window, "standaloneEngineChoice").property("currentText") == "ROUTED"
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
    target = find(window, "standaloneEngineChoice")
    parent = target.parentItem()
    while parent.metaObject().indexOfProperty("contentY") < 0:
        parent = parent.parentItem()
    offset = target.mapToItem(parent.property("contentItem"), QPointF(0, 0)).y()
    parent.setProperty("contentY", max(0, offset - 60))
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
    capture(window, output / "curve-engine.png")
    history(controller, window, curve.id)
    controller.authoring.setEditing(True)
    target(controller, window, fiber.id)
    capture(window, output / "fiber-engine.png")
    select(controller, window, curve.id, "ROUTED")
    switch_back(controller, window, curve.id)
    cancel_preview(controller, curve.id)
    primitive_engine(controller, window, curve.id)


def primitive_engine(controller, window, key):
    parent = controller.session.document.entities[0].id
    args = dict(curves=[key], kind="BODY", parent=parent)
    consumer = controller.run("primitive.from_curves", args)
    assert consumer, controller.message
    settle(controller)
    controller.selection_view.select(consumer)
    controller.authoring.setEditing(True)
    settle(controller)
    choose(window, 1, "primitiveEngineChoice")
    settle(controller)
    assert controller.session.document.object(key).engine == "POLYLINE"
    child = controller.session.command("scp.empty", name="Locking child", parent=consumer)
    settle(controller)
    locked_engine(controller, window, key, child)


def locked_engine(controller, window, key, child):
    control = selector(window, "primitiveEngineChoice")
    assert not control.property("enabled")
    control.setProperty("currentIndex", 2)
    assert QMetaObject.invokeMethod(control, "activated", Qt.DirectConnection, Q_ARG(int, 2))
    settle(controller)
    assert controller.session.document.object(key).engine == "POLYLINE"
    assert control.property("currentText") == "POLYLINE"
    assert child in controller.message
    controller.run("scp.delete", dict(entity=child))
    settle(controller)
    assert control.property("enabled")


def switch_back(controller, window, key):
    before, cursor = controller.session.document.object(key), controller.session.history.cursor
    choose(window, 0)
    settle(controller)
    assert controller.session.document.object(key).points == before.points
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    assert find(window, "standaloneEngineChoice").property("currentText") == "ROUTED"
    cursor = controller.session.history.cursor
    choose(window, 2)
    settle(controller)
    assert controller.session.history.cursor == cursor


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
        print(
            "Direct Curve/Fiber engines, retained points, selector synchronization and undo passed."
        )
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    output = Path("build/direct-curve-engine")
    output.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(Path(sys.argv[1]), output)
