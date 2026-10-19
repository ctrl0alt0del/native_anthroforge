"""0.2.1 full-QML large-list and placement qualification; offscreen only."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

import json
from pathlib import Path
from zipfile import ZipFile

from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from routing_scale_probe import scene
from shiboken6 import delete
from ui_acceptance import find
from ui_polish_acceptance import descendants

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/021-curve-workflows")


def settle(controller):
    controller.session.wait(30)
    controller.refresh()
    QTest.qWait(80)


def click(window, name):
    assert QMetaObject.invokeMethod(find(window, name), "clicked", Qt.DirectConnection)
    QGuiApplication.processEvents()


def setup(controller):
    scene(controller.session, 120)
    keys = [item.id for item in controller.session.document.entities]
    for key in keys[:2]:
        controller.session.command("scp.rename", entity=key, name="Cube")
    points = [dict(position=(-2 + 4 * i / 119, -2, 0)) for i in range(120)]
    key = controller.run("curve.create", dict(points=points))
    settle(controller)
    controller.select(key)
    controller.authoring.setEditing(True)
    settle(controller)
    return key


def reveal(window, name, file):
    target = find(window, name)
    parent = target.parentItem()
    while parent.metaObject().indexOfProperty("contentY") < 0:
        parent = parent.parentItem()
    offset = target.mapToItem(parent.property("contentItem"), QPointF()).y()
    parent.setProperty("contentY", max(0, offset - 12))
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / file))


def points(window, controller):
    find(window, "curveConversionToggle").setProperty("checked", True)
    find(window, "conversionEngine").setProperty("currentIndex", 2)
    find(window, "conversionPointToggle").setProperty("checked", True)
    QTest.qWait(50)
    model = find(window, "conversionPoint").property("choices")
    assert model.counts == dict(total=120, chosen=120, shown=120)
    check_virtualization(window, "conversionPointChoice")
    search = find(window, "conversionPointSearch")
    search.setProperty("text", "Point 11")
    click(window, "conversionPointClearShown")
    assert model.counts["chosen"] == 109 and model.counts["shown"] == 11
    click(window, "conversionPointReset")
    assert model.counts["chosen"] == 120 and search.property("text") == "Point 11"
    point_focus(window, controller, model, search)


def point_focus(window, controller, model, search):
    search.setProperty("text", "Point 1")
    click(window, "conversionPointClearShown")
    assert model.records.rows[0]["chosen"] and model.records.rows[-1]["chosen"]
    click(window, "conversionPointReset")
    search.setProperty("text", "")
    find(window, "conversionPointList").setProperty("contentY", 4000)
    QTest.qWait(80)
    check_virtualization(window, "conversionPointChoice")
    focus_visible_point(window, controller)
    scroll = find(window, "conversionPointList").property("contentY")
    click(window, "conversionPointReset")
    assert find(window, "conversionPointList").property("contentY") == scroll
    reveal(window, "conversionPoint", "points-120.png")


def focus_visible_point(window, controller):
    row = next(
        r
        for r in descendants(window.contentItem())
        if r.objectName() == "conversionPointChoice" and r.isEnabled()
    )
    row.setProperty("checked", False)
    assert QMetaObject.invokeMethod(row, "clicked", Qt.DirectConnection)
    assert controller.authoring.selectedComponent["point"] == row.property("targetId")


def check_virtualization(window, name):
    rows = [r for r in descendants(window.contentItem()) if r.objectName() == name]
    assert 0 < len(rows) <= 24, (name, len(rows))  # Includes Qt's retained reuse pool.


def obstacles(window):
    find(window, "conversionObstacleToggle").setProperty("checked", True)
    QTest.qWait(50)
    model = find(window, "conversionObstacle").property("choices")
    assert model.counts == dict(total=120, chosen=0, shown=120)
    assert model.records.rows[0]["detail"] != model.records.rows[1]["detail"]
    search = find(window, "conversionObstacleSearch")
    search.setProperty("text", "Cube")
    click(window, "conversionObstacleChooseShown")
    assert model.counts["chosen"] == model.counts["shown"]
    search.setProperty("text", "")
    click(window, "conversionObstacleReset")
    assert model.counts["chosen"] == 0
    check_virtualization(window, "conversionObstacleChoice")
    reveal(window, "conversionObstacle", "obstacles-120.png")


def preview(window, controller, key):
    before = controller.session.document.object(key)
    click(window, "previewCurveConversion")
    settle(controller)
    assert controller.session.conversion.state == "ready", controller.session.conversion.error
    click(window, "acceptCurveConversion")
    settle(controller)
    item = controller.session.document.object(key)
    assert item.engine == "ROUTED" and len(item.points) == 120 and item.result.status == "ready"
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(key).points == before.points
    assert controller.session.document.object(key).engine == "BEZIER"


def report(controller):
    path = OUTPUT / "large-lists.afprofile.zip"
    controller.session.command("profile.stop", path=str(path), wait=True)
    with ZipFile(path) as archive:
        summary = json.loads(archive.read("summary.json"))
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2))


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profiler, controller, warnings = QtProfiler(), Controller(), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        window, key = engine.rootObjects()[0], setup(controller)
        exercise(window, controller, key)
        assert not warnings, warnings
        print("120-point / 120-obstacle QML editors, virtualization, preview and undo passed.")
    finally:
        close(controller, engine, profiler)


def exercise(window, controller, key):
    controller.session.command("profile.start")
    points(window, controller)
    obstacles(window)
    preview(window, controller, key)
    placement(window, controller)
    report(controller)


def placement(window, controller):
    click(window, "placeCurvePoints")
    tool = controller.drawing_tools
    before, cursor = len(controller.session.document.objects), controller.session.history.cursor
    place_click(window, 0.35, 0.42)
    assert tool.mode == "POINTS" and tool.state["count"] == 1
    QTest.keyClick(window, Qt.Key_1)
    assert tool.mode == "POINTS" and tool.state["count"] == 1
    place_click(window, 0.50, 0.48, Qt.ShiftModifier)
    assert tool.mode == "POINTS" and tool.state["count"] == 2
    place_click(window, 0.65, 0.55)
    settle(controller)
    assert not tool.mode and len(controller.session.document.objects) == before + 1
    assert controller.session.history.cursor == cursor + 1
    placement_undo(window, controller, before)


def place_click(window, x, y, modifiers=Qt.NoModifier):
    viewport = find(window, "viewport")
    point = viewport.mapToScene(QPointF(viewport.width() * x, viewport.height() * y))
    QTest.mouseClick(window, Qt.LeftButton, modifiers, point.toPoint())
    QGuiApplication.processEvents()


def placement_undo(window, controller, count):
    controller.run("undo", {})
    settle(controller)
    assert len(controller.session.document.objects) == count
    click(window, "placeCurvePoints")
    place_click(window, 0.3, 0.4)
    QTest.keyClick(window, Qt.Key_Escape)
    assert not controller.drawing_tools.mode and len(controller.session.document.objects) == count


def close(controller, engine, profiler):
    controller.close()
    delete(engine)
    profiler.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run()
