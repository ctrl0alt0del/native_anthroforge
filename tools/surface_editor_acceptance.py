"""Full-QML surface creation, inspector operations and retained staged geometry, offscreen."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.core.surfaces import Surface
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QGuiApplication.processEvents()


def sources(controller):
    keys = [
        controller.run("curve.create", dict(points=[dict(position=[x, y, 0]) for x in (-0.5, 0.5)]))
        for y in (-0.2, 0.2)
    ]
    settle(controller)
    controller.select(keys[0])
    controller.select(keys[1], True)
    return keys


def action(engine, name, signal):
    window = engine.rootObjects()[0]
    item = find(window, name)
    assert item is not None, name
    assert QMetaObject.invokeMethod(item, signal, Qt.DirectConnection)


def create(controller, engine):
    keys = sources(controller)
    action(engine, "createLoftSurface", "triggered")
    settle(controller)
    surface = next(o for o in controller.session.document.objects if isinstance(o, Surface))
    controller.select(surface.id)
    settle(controller)
    assert controller.selectedData["kind"] == "SURFACE" and not controller.treeRows
    assert any(row["id"] == surface.id for row in controller.render_model.wanted.values())
    assert controller.authoring.state["uses"][0]["curve"] == keys[0]
    return surface.id


def inspection(controller, engine, target):
    action(engine, "surfaceRealign", "clicked")
    settle(controller)
    assert controller.session.document.object(target).result.status == "ready"
    window = engine.rootObjects()[0]
    button = find(window, "surfaceFlip")
    button.setProperty("checked", True)
    action(engine, "surfaceFlip", "clicked")
    settle(controller)
    assert controller.session.document.object(target).flip
    controller.run("undo", {})
    settle(controller)
    assert not controller.session.document.object(target).flip
    independence(controller, engine, target)


def independence(controller, engine, target):
    previous = controller.session.document.object(target).curves[0].curve
    action(engine, "surfaceIndependent0", "clicked")
    settle(controller)
    changed = controller.session.document.object(target).curves[0].curve
    assert changed != previous and previous in controller.session.document.registry.records


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        target = create(controller, engine)
        inspection(controller, engine, target)
        assert not warnings, warnings
        assert not controller.message, controller.message
        print("Offscreen surface menu, inspector, Realign, undo and mesh staging passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
