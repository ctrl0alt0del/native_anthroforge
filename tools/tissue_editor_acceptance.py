"""Tissue desktop entry points and inspector offscreen; never uses desktop input."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QTest.qWait(100)


def fiber(controller, bone, y):
    source = controller.run(
        "curve.create",
        dict(points=[dict(position=p) for p in [[-0.4, y, 0.6], [0, y, 0.7], [0.4, y, 0.6]]]),
    )
    settle(controller)
    points = controller.session.document.object(source).points
    controller.construction_view.createConstruction(
        "fiber.create",
        dict(
            curve=source, bindings=[dict(point=p.id, target=bone) for p in (points[0], points[-1])]
        ),
    )
    settle(controller)
    return controller.selection


def scene(controller):
    path = str(Path("examples/primitives/cube.obj").resolve())
    bone = controller.run("import", dict(path=path, units=1.0))["entity_id"]
    settle(controller)
    sources = [fiber(controller, bone, y) for y in (-0.2, 0.2)]
    controller.construction_view.createConstruction(
        "surface.create", dict(curves=sources, kind="LOFT")
    )
    settle(controller)
    assert controller.selection_view.selectedData["kind"] == "MEMBRANE"


def exercise(controller, window):
    scene(controller)
    button = find(window, "createTissue")
    assert button.property("visible") and button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    settle(controller)
    assert controller.selection_view.selectedData["is_tissue"]
    target = controller.selection
    controller.run("tissue.configure", dict(target=target, changes=dict(stacking=False)))
    settle(controller)
    assert controller.selection_view.selectedData["status"] == "ready"
    assert not controller.selection_view.selectedData["transformable"]
    assert find(window, "tissueInflationAmount").property("visible")


def run(scenario=exercise):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(400)
        scenario(controller, window)
        output = Path("build/022-tissue")
        output.mkdir(parents=True, exist_ok=True)
        assert window.grabWindow().save(str(output / "tissue-inspector.png"))
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run()
            print("Tissue offscreen creation, selection and ordinary-loft inspector passed.")
        finally:
            delete(app)
