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
from snapped_routing_acceptance import choose
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
    key = controller.selection
    before, cursor = controller.session.document.object(key), controller.session.history.cursor
    choose(window, 2)
    settle(controller)
    item = controller.session.document.object(key)
    assert item.engine == "ROUTED" and item.points == before.points and len(item.points) == 120
    assert item.result.status == "ready", item.result.error
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(key).engine == "BEZIER"
    controller.run("redo", {})
    settle(controller)
    reveal(window, "standaloneEngineChoice", "points-120.png")


def check_virtualization(window, name):
    rows = [r for r in descendants(window.contentItem()) if r.objectName() == name]
    assert 0 < len(rows) <= 24, (name, len(rows))  # Includes Qt's retained reuse pool.


def obstacles(window):
    find(window, "routingObstacleToggle").setProperty("checked", True)
    QTest.qWait(50)
    model = find(window, "routingObstacle").property("choices")
    assert model.counts == dict(total=120, chosen=0, shown=120)
    assert model.records.rows[0]["detail"] != model.records.rows[1]["detail"]
    search = find(window, "routingObstacleSearch")
    search.setProperty("text", "Cube")
    click(window, "routingObstacleChooseShown")
    assert model.counts["chosen"] == model.counts["shown"]
    search.setProperty("text", "")
    click(window, "routingObstacleReset")
    assert model.counts["chosen"] == 0
    check_virtualization(window, "routingObstacleChoice")
    reveal(window, "routingObstacle", "obstacles-120.png")


def report(controller):
    path = OUTPUT / "large-lists.afprofile.zip"
    controller.session.command("profile.stop", path=str(path), wait=False)
    await_export(controller)
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        capture_completeness(manifest)
        summary = json.loads(archive.read("summary.json"))
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2))


def capture_completeness(manifest):
    assert manifest["qt"]["finished"] and not manifest["qt"]["failure"], manifest
    assert all(manifest["capabilities"][key] for key in ("qml", "tasks", "model_changes"))
    if not manifest["complete"]:
        loss = dict(evicted=manifest["storage"]["evicted"], qt_dropped=manifest["qt"]["dropped"])
        assert any(loss.values()), manifest
        print("Stress trace is incomplete due to bounded capture; timing totals are partial:", loss)


def await_export(controller):
    for _ in range(400):
        if controller.session.profiler.done.is_set():
            break
        QTest.qWait(25)
    assert controller.session.profiler.state == "saved", controller.session.profiler.status()


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profiler, controller, warnings = QtProfiler(), Controller(), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        setup(controller)
        exercise(window, controller)
        assert not warnings, warnings
        print(
            "120 retained points / 120 obstacles, direct engines, virtualization and undo passed."
        )
    finally:
        close(controller, engine, profiler)


def exercise(window, controller):
    controller.session.command("profile.start")
    points(window, controller)
    obstacles(window)
    settle(controller)
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
        try:
            run()
        finally:
            delete(app)
