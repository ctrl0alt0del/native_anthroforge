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
        assert not warnings, warnings
        print("Offscreen desktop fiber creation, Construction entry and staged path passed.")
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


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
