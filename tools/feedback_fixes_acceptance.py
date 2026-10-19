"""Exercise all three October 19 reports through offscreen QML and native projection."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

import json
from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QCoreApplication, QMetaObject, QPointF, Qt, QUrl
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from report_browser_acceptance import wait_for
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.application.curve_sources import world
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.native.strokes import plane

OUTPUT = Path("build/three-reports-acceptance")


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QTest.qWait(100)


def setup(controller):
    result = controller.run("import", dict(path="examples/primitives/cube.obj", units=1.0))
    settle(controller)
    target = result["entity_id"]
    controller.select(target)
    return target


def axis_view(window, name):
    viewport = find(window, "viewport")
    QMetaObject.invokeMethod(viewport, "setView", Q_ARG("QVariant", name))
    QTest.qWait(80)
    return viewport


def projected(window, x, y, z=0.5):
    viewport = find(window, "viewport")
    local = QMetaObject.invokeMethod(
        viewport,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        Q_ARG(float, x),
        Q_ARG(float, y),
        Q_ARG(float, z),
    )
    return viewport.mapToScene(local).toPoint()


def placement(window, controller):
    viewport = axis_view(window, "Top")
    assert viewport.property("imageAlignmentAxis") == "Z"
    click(window, "placeCurvePoints")
    point = projected(window, -0.2, -0.2)
    QTest.mouseMove(window, point)
    QTest.keyPress(window, Qt.Key_Control)
    tool = controller.drawing_tools
    np.testing.assert_allclose(tool.hover, [-0.2, -0.2, 0.5], atol=0.005)
    assert tool.state["count"] == 0
    QTest.keyRelease(window, Qt.Key_Control)
    QCoreApplication.processEvents()
    assert abs(tool.hover[2]) < 1e-6, (tool.hover, tool.snapping)
    placement_commit(window, controller)


def placement_commit(window, controller):
    cursor = controller.session.history.cursor
    modifiers = Qt.ControlModifier | Qt.ShiftModifier
    for x, y in ((-0.2, -0.2), (0.2, 0.0)):
        QTest.mouseClick(window, Qt.LeftButton, modifiers, projected(window, x, y))
    assert controller.drawing_tools.state["count"] == 2
    QTest.mouseClick(window, Qt.LeftButton, Qt.ControlModifier, projected(window, 0.1, 0.2))
    settle(controller)
    curve = controller.session.document.object(controller.selection)
    np.testing.assert_allclose([p.position[2] for p in curve.points], [0.5] * 3)
    assert controller.session.history.cursor == cursor + 1 and not controller.drawing_tools.mode
    assert find(window, "constructionTab").property("checked")
    controller.run("undo", {})
    settle(controller)
    assert curve.id not in controller.session.document.registry.records


def remapped_snap(window, controller):
    keyboard = find(window, "keyboardManager")
    bindings = keyboard.property("modifierBindings").toVariant()
    bindings["snapSurface"] = Qt.AltModifier.value
    keyboard.setProperty("modifierBindings", bindings)
    click(window, "placeCurvePoints")
    point = projected(window, 0.2, 0.2)
    QTest.mouseMove(window, point)
    QTest.keyPress(window, Qt.Key_Alt)
    assert abs(controller.drawing_tools.hover[2] - 0.5) < 1e-9
    QTest.mouseClick(window, Qt.LeftButton, Qt.AltModifier | Qt.ShiftModifier, point)
    QTest.keyRelease(window, Qt.Key_Alt)
    QTest.keyClick(window, Qt.Key_Escape)
    assert not controller.drawing_tools.mode and not controller.session.document.objects


def accept_image(window, controller):
    path = OUTPUT / "reference.png"
    Image.new("RGB", (240, 120), "#5b7496").save(path)
    picker = find(window, "referenceImageDialog")
    picker.setProperty("selectedFile", QUrl.fromLocalFile(str(path.resolve())))
    assert QMetaObject.invokeMethod(picker, "accept")
    wait_for(lambda: bool(controller.session.document.registry.construction))
    settle(controller)
    return controller.session.document.object(controller.selection)


def image_imports(window, controller, root):
    controller.select(root)
    controller.run("scp.transform", dict(entity=root, values=[1, 2, 3, 20, 50, 10, 1, 1, 1]))
    settle(controller)
    axis_view(window, "Right")
    click(window, "addObjectImage")
    assert controller.image_tools.import_request[1]["parent"] == root
    item = accept_image(window, controller)
    assert item.parent == root and item.owners == (root,)
    check_import_result(window, controller, item, root)


def check_import_result(window, controller, item, root):
    actual = plane(
        controller.session.engine,
        world(controller.session.engine, controller.session.document, item.id),
    )
    np.testing.assert_allclose(actual, [1, 2, 3, 1, 0, 0], atol=1e-9)
    assert not find(window, "addObjectImage").isVisible()
    assert find(window, "constructionTab").property("checked")
    world_import(window, controller, root)


def world_import(window, controller, root):
    controller.select(root)
    axis_view(window, "Front")
    click(window, "addWorldImage")
    request = controller.image_tools.import_request[1]
    assert request["parent"] == "" and request["axis"] == "Y"
    picker = find(window, "referenceImageDialog")
    QMetaObject.invokeMethod(picker, "reject")
    assert controller.image_tools.import_request is None
    assert find(window, "anatomyTab").property("checked")


def tabs_and_captures(window):
    for width, height in ((1440, 900), (1050, 680)):
        window.setWidth(width)
        window.setHeight(height)
        for tab, content in (("anatomyTab", "hierarchy"), ("constructionTab", "constructionList")):
            click(window, tab)
            assert find(window, content).isVisible()
            assert find(window, content).height() > height * 0.45
            assert window.grabWindow().save(str(OUTPUT / f"{tab}-{width}.png"))


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        exercise(engine.rootObjects()[0], controller)
        assert not warnings, warnings
        print(json.dumps(dict(passed=True, tabs=True, image_imports=True, snap_modifiers=True)))
    finally:
        controller.close()
        delete(engine)


def exercise(window, controller):
    root = setup(controller)
    placement(window, controller)
    remapped_snap(window, controller)
    image_imports(window, controller, root)
    tabs_and_captures(window)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_DontUseNativeDialogs, True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
