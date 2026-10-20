"""Exercise alternate tools, point preview and surface grouping through actual offscreen QML."""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtTest import QTest
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    settle,
)
from ui_acceptance import click, find

from tests.test_branch_creation import curve
from tests.test_surface_grouping import ambiguous

OUTPUT = Path("build/branched-point-placement")


def project(window, position):
    viewport = find(window, "viewport")
    pixel = QMetaObject.invokeMethod(
        viewport, "projectPoint", Q_RETURN_ARG(QPointF), *(Q_ARG(float, float(v)) for v in position)
    )
    return viewport.mapToScene(pixel).toPoint()


def menu(controller, window):
    button = find(window, "placeCurvePoints")
    center = button.mapToScene(QPointF(button.width() / 2, button.height() / 2)).toPoint()
    QTest.mouseClick(window, Qt.RightButton, pos=center)
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / "alternate-tools.png"))
    click(window, "branchedPointPlacement")
    assert controller.drawing_tools.mode == "BRANCH"


def placement(controller, window):
    source = curve(controller.session)
    settle(controller)
    controller.cameraRequested.emit([0.5, 1.5, 0, -90, 0, 0, 5], True)
    QTest.qWait(200)
    menu(controller, window)
    before = controller.session.history.cursor
    point = project(window, [0.05, 1.05, 0])
    QTest.mouseMove(window, point)
    QTest.qWait(80)
    assert controller.drawing_tools.hover == [0.0, 1.0, 0.0]
    assert find(window, "placementPreview").isVisible()
    assert window.grabWindow().save(str(OUTPUT / "root-preview.png"))
    complete(controller, window, point, source, before)


def complete(controller, window, first, source, before):
    QTest.mouseClick(window, Qt.LeftButton, pos=first)
    assert not controller.session.document.junctions
    QTest.mouseClick(window, Qt.LeftButton, Qt.ShiftModifier, pos=project(window, [0.6, 1.2, 0]))
    assert controller.drawing_tools.mode == "BRANCH"
    QTest.mouseClick(window, Qt.LeftButton, pos=project(window, [1, 1.3, 0]))
    settle(controller)
    assert not controller.drawing_tools.mode
    assert controller.session.history.cursor == before + 1
    assert len(controller.session.document.objects[-1].points) == 3
    assert controller.session.document.object(source).points[1].junction
    assert window.grabWindow().save(str(OUTPUT / "placed-branch.png"))
    controller.run("undo", {})
    settle(controller)
    assert not controller.session.document.junctions


def grouping(controller, window):
    keys = ambiguous(controller.session)
    settle(controller)
    for index, key in enumerate(keys):
        controller.select(key, index > 0)
    click(window, "createPatchSurface")
    QTest.qWait(100)
    assert window.property("modalOpen")
    assert window.grabWindow().save(str(OUTPUT / "ambiguous-groups.png"))
    choose_split(controller, window, keys)


def choose_split(controller, window, keys):
    for index in (4, 5):
        combo = find(window, "surfaceGroupRole" + str(index))
        combo.setProperty("currentIndex", 2)
        QMetaObject.invokeMethod(combo, "activated", Q_ARG(int, 2))
    click(window, "confirmSurfaceGrouping")
    settle(controller)
    assert not window.property("modalOpen")
    item = controller.session.document.object(controller.selection)
    assert item.kind == "BRANCHED" and len(item.branches) == 2
    assert set(u.curve for u in item.curves) == set(keys)


def exercise(controller, window):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    placement(controller, window)
    grouping(controller, window)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(exercise)
            print("Offscreen branch menu, preview, Shift continuation, undo and grouping passed.")
        finally:
            delete(app)
