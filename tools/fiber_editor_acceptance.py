"""Exercise the desktop fiber-creation entry point without opening a desktop window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import numpy as np
from PySide6.QtCore import QMetaObject, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete

from anthroforge.core.fibers import Fiber
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QGuiApplication.processEvents()


def setup(controller):
    controller.run("import", dict(path="examples/primitives/cube.obj", units=1.0))
    settle(controller)
    source = controller.run("curve.create", {})
    settle(controller)
    controller.select(source)
    controller.authoring.setEditing(True)
    settle(controller)
    return source


def create(controller, engine):
    source = setup(controller)
    window = engine.rootObjects()[0]
    buttons = window.findChildren(QObject, "createFiberFromCurve")
    button = next(item for item in buttons if item.property("sourceId") == source)
    assert button and button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    fibers = [o for o in controller.session.document.objects if isinstance(o, Fiber)]
    assert len(fibers) == 1, controller.message
    assert fibers[0].id != source and controller.constructionModel.rowCount() == 2
    assert any(row["id"] == fibers[0].id for row in controller.path_model.wanted.values())
    controller.select(fibers[0].id)
    settle(controller)
    assert controller.selectedData["kind"] == "FIBER"


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        create(controller, engine)
        editing(controller)
        bindings(controller, engine)
        conversion(controller, engine)
        assert not warnings, warnings
        print("Offscreen desktop fiber creation, binding edits, gestures and staged path passed.")
    finally:
        controller.close()
        delete(engine)


def editing(controller):
    fiber = controller.selection
    target = controller.session.document.entities[0].id
    controller.run("scp.transform", dict(entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1]))
    settle(controller)
    revision = controller.session.document.revision
    controller.authoring.setEditing(True)
    row = next(r for r in controller.authoring.componentRows if r["part"] == "position")
    assert row["world"][2] > 0.9 and controller.session.document.revision == revision
    controller.authoring.selectComponent(row["key"], False)
    drag(controller, fiber, row["world"])


def drag(controller, fiber, opening):
    cursor = controller.session.history.cursor
    assert controller.beginTransform("Move")
    controller.transformDelta([0, 0.2, 0, 0, 0, 0, 1, 1, 1])
    controller.endTransform(False)
    settle(controller)
    item = controller.session.document.object(fiber)
    assert item.result.status == "ready", item.result.error
    np.testing.assert_allclose(item.points[0].position, np.array(opening) + [0, 0.2, 0])
    assert controller.session.history.cursor == cursor + 1
    undo_drag(controller, fiber, opening)


def undo_drag(controller, fiber, opening):
    controller.run("undo", {})
    settle(controller)
    asset = controller.session.resources.paths[
        controller.session.document.object(fiber).result.asset
    ]
    np.testing.assert_allclose(asset.path.array()[0, :3], opening)


def bindings(controller, engine):
    fiber = controller.selection
    controller.run(
        "curve.point.insert", dict(curve=fiber, index=1, point=dict(position=[0, 0.2, 1]))
    )
    settle(controller)
    select_interior(controller, fiber)
    click_binding(controller, engine, "setFiberBinding")
    assert len(controller.session.document.object(fiber).bindings) == 3
    click_binding(controller, engine, "removeFiberBinding")
    assert len(controller.session.document.object(fiber).bindings) == 2


def select_interior(controller, fiber):
    point = controller.session.document.object(fiber).points[1].id
    row = next(
        r
        for r in controller.authoring.componentRows
        if r["point"] == point and r["part"] == "position"
    )
    controller.authoring.selectComponent(row["key"], False)
    settle(controller)


def click_binding(controller, engine, name):
    from ui_acceptance import find

    button = find(engine.rootObjects()[0], name)
    assert button.property("enabled") and QMetaObject.invokeMethod(
        button, "clicked", Qt.DirectConnection
    )
    settle(controller)


def conversion(controller, engine):
    from ui_acceptance import find

    click_binding(controller, engine, "setFiberBinding")
    find(engine.rootObjects()[0], "conversionEngine").setProperty("currentIndex", 1)
    click_binding(controller, engine, "previewCurveConversion")
    assert controller.session.conversion.state == "ready", controller.session.conversion.error
    click_binding(controller, engine, "acceptCurveConversion")
    item = controller.session.document.object(controller.selection)
    assert item.engine == "POLYLINE" and len(item.bindings) == 3
    assert item.result.status == "ready", item.result.error


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
