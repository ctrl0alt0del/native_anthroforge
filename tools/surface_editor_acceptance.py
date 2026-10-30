"""Full-QML surface creation, inspector operations and retained staged geometry, offscreen."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.core.surfaces import Surface
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
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
    controller.selection_view.select(keys[0])
    controller.selection_view.select(keys[1], True)
    return keys


def action(engine, name, signal):
    window = engine.rootObjects()[0]
    item = find(window, name)
    assert item is not None, name
    assert QMetaObject.invokeMethod(item, signal, Qt.DirectConnection)


def create(controller, engine):
    keys = sources(controller)
    click(engine.rootObjects()[0], "createPatchSurface")
    settle(controller)
    surface = next(o for o in controller.session.document.objects if isinstance(o, Surface))
    assert controller.selection == surface.id and not controller.authoring.editing
    settle(controller)
    assert (
        controller.selection_view.selectedData["kind"] == "SURFACE"
        and not controller.selection_view.treeRows
    )
    assert any(row["id"] == surface.id for row in controller.render_model.wanted.values())
    assert controller.authoring.state["uses"][0]["curve"] == keys[0]
    return surface.id


def inspection(controller, engine, target):
    select_sources(controller, engine, target)
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


def select_sources(controller, engine, target):
    before = controller.session.document
    expected = controller.session.command("surface.source_ids", target=target)
    action(engine, "selectAllSurfaceSources", "clicked")
    settle(controller)
    assert controller.selection_view.selectedObjects == expected
    assert controller.session.document is before
    controller.selection_view.select(target)
    settle(controller)


def realign(controller, engine):
    before = len(controller.session.history.entries)
    action(engine, "surfaceRealign", "clicked")
    settle(controller)
    assert not controller.construction_view.surfacePreview["token"]
    assert len(controller.session.history.entries) == before + 1


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
        additional_sources(controller, engine)
        closed_creation(controller, engine)
        assert not warnings, warnings
        assert not controller.message, controller.message
    finally:
        controller.close()
        delete(engine)


def closed_creation(controller, engine):
    from surface_preview_scene import sources

    curves = sources(controller)
    controller.selection_view.select(curves[0])
    controller.selection_view.select(curves[1], True)
    before = len(controller.session.document.objects)
    click(engine.rootObjects()[0], "createPatchSurface")
    settle(controller)
    assert not controller.construction_view.surfacePreview["token"]
    assert len(controller.session.document.objects) == before + 1


def additional_sources(controller, engine):
    keys = sources(controller)
    third = controller.run(
        "curve.create", dict(points=[dict(position=[x, 0.6, 0]) for x in (-0.5, 0.5)])
    )
    settle(controller)
    controller.selection_view.select(third, True)
    assert controller.selection_view.selectedObjects == [*keys, third]
    assert controller.construction_view.surfaceAction["enabled"]
    click(engine.rootObjects()[0], "createPatchSurface")
    settle(controller)
    surface = controller.session.document.object(controller.selection)
    assert [use.curve for use in surface.curves] == [*keys, third]
    assert surface.kind == "LOFT" and surface.result.status == "ready"
    assert_surface_undo(controller, surface)


def assert_surface_undo(controller, surface):
    controller.run("undo", {})
    assert surface.id not in controller.session.document.registry.records


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
            print("Offscreen surface creation, inspector, Realign, undo and mesh staging passed.")
        finally:
            delete(app)
