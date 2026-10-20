"""Exercise the desktop fiber-creation entry point without opening a desktop window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from pathlib import Path

import numpy as np
from PySide6.QtCore import QMetaObject, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

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
    assert controller.selection == fibers[0].id and not controller.authoring.active
    assert controller.selectedData["kind"] == "FIBER" and not controller.authoring.selection


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        exercise(controller, engine)
        assert not warnings, warnings
        print("Offscreen desktop fiber creation, binding edits, gestures and staged path passed.")
    finally:
        controller.close()
        delete(engine)


def exercise(controller, engine):
    create(controller, engine)
    object_transform_policy(controller, engine.rootObjects()[0])
    editing(controller)
    component_shortcuts(controller, engine.rootObjects()[0])
    bindings(controller, engine)
    conversion(controller, engine)


def object_transform_policy(controller, window):
    viewport = find(window, "viewport")
    before, cursor = controller.session.document, controller.session.history.cursor
    mode, selection = window.property("activeTool"), controller.selection
    assert not viewport.property("transformAvailable")
    assert not find(window, "transformGizmo").isVisible()
    assert not find(window, "objectTransform").isEnabled()
    disabled_tools(window)
    rejected_shortcuts(window, viewport)
    assert controller.selection == selection
    assert window.property("activeTool") == mode and controller.session.document == before
    assert controller.session.history.cursor == cursor and controller.session.history.before is None
    capture(window)


def disabled_tools(window):
    for name in ("Move", "Rotate", "Scale"):
        assert not find(window, "tool" + name).isEnabled()
        click(window, "tool" + name)


def capture(window):
    output = Path("build/fiber-transform-policy/fiber-object.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    assert window.grabWindow().save(str(output))


def rejected_shortcuts(window, viewport):
    keyboard, requested = find(window, "keyboardManager"), []
    keyboard.requested.connect(requested.append)
    viewport.forceActiveFocus()
    for key in (Qt.Key_G, Qt.Key_R, Qt.Key_S, Qt.Key_W, Qt.Key_E):
        QTest.keyClick(window, key)
        assert not find(window, "modalTransform").property("active")
    keyboard.requested.disconnect(requested.append)
    assert not requested


def component_shortcuts(controller, window):
    viewport = find(window, "viewport")
    assert viewport.property("transformAvailable")
    assert all(find(window, "tool" + mode).isEnabled() for mode in ("Move", "Rotate", "Scale"))
    before, cursor = controller.session.document, controller.session.history.cursor
    for key in (Qt.Key_G, Qt.Key_R, Qt.Key_S):
        viewport.forceActiveFocus()
        QTest.keyClick(window, key)
        assert find(window, "modalTransform").property("active")
        QTest.keyClick(window, Qt.Key_Escape)
        assert not find(window, "modalTransform").property("active")
    assert controller.session.document == before and controller.session.history.cursor == cursor


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
    from snapped_routing_acceptance import choose

    click_binding(controller, engine, "setFiberBinding")
    choose(engine.rootObjects()[0], 1)
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert item.engine == "POLYLINE" and len(item.bindings) == 3
    assert item.result.status == "ready", item.result.error


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
