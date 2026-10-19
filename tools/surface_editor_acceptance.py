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
    controller.createSurface("LOFT")  # Generic surface API remains; redundant menu was retired.
    settle(controller)
    surface = next(o for o in controller.session.document.objects if isinstance(o, Surface))
    controller.select(surface.id)
    settle(controller)
    assert controller.selectedData["kind"] == "SURFACE" and not controller.treeRows
    assert any(row["id"] == surface.id for row in controller.render_model.wanted.values())
    assert controller.authoring.state["uses"][0]["curve"] == keys[0]
    return surface.id


def inspection(controller, engine, target):
    realign(controller, engine)
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


def realign(controller, engine):
    action(engine, "surfaceRealign", "clicked")
    settle(controller)
    assert controller.surfacePreview["state"] == "ready"
    action(engine, "surfacePreviewAccept", "clicked")
    settle(controller)


def independence(controller, engine, target):
    previous = controller.session.document.object(target).curves[0].curve
    action(engine, "surfaceIndependent0", "clicked")
    settle(controller)
    changed = controller.session.document.object(target).curves[0].curve
    assert changed != previous and previous in controller.session.document.registry.records


def source_list(controller, engine, target):
    source = controller.run("curve.create", dict(name="Additional source"))
    settle(controller)
    window = engine.rootObjects()[0]
    combo = find(window, "surfaceNewSource")
    combo.setProperty("currentIndex", combo.property("count") - 1)
    action(engine, "surfaceAddSource", "clicked")
    settle(controller)
    assert controller.session.document.object(target).curves[-1].curve == source
    find(window, "surfaceSourceChoice").setProperty("currentIndex", 2)
    action(engine, "surfaceRemoveSource", "clicked")
    settle(controller)
    assert len(controller.session.document.object(target).curves) == 2
    assert source in controller.session.document.registry.records


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        target = create(controller, engine)
        inspection(controller, engine, target)
        source_list(controller, engine, target)
        closed_preview(controller, engine)
        assert not warnings, warnings
        assert not controller.message, controller.message
        print("Offscreen surface creation, inspector, Realign, undo and mesh staging passed.")
    finally:
        controller.close()
        delete(engine)


def closed_preview(controller, engine):
    from surface_preview_scene import sources

    curves = sources(controller)
    controller.select(curves[0])
    controller.select(curves[1], True)
    before = len(controller.session.document.objects)
    controller.createSurface("LOFT")
    settle(controller)
    assert len(controller.session.document.objects) == before
    assert controller.surfacePreview["state"] == "ready", controller.surfacePreview
    action(engine, "surfacePreviewAccept", "clicked")
    settle(controller)
    assert len(controller.session.document.objects) == before + 1


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
