"""Real surface ruler input, camera restoration and frozen measurement reports."""

import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from curve_interaction_acceptance import screen
from PySide6.QtCore import QPoint, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find
from view_gesture_acceptance import begin_modal, check_undo, key, position, select_point
from workflow_acceptance import settle

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/inspection-018").resolve()


def fixture(controller):
    result = controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1)
    )
    settle(controller)
    controller.select(result["entity_id"])
    controller.cameraRequested.emit([0, 0, 0, 0, 0, 0, 3], True)
    QTest.qWait(100)
    return result["entity_id"]


def ruler(controller, window):
    cursor = controller.session.history.cursor
    click(window, "measureSurface")
    for point in ([-0.25, -0.5, 0], [0.25, -0.5, 0]):
        position = screen(window, point)
        QTest.mouseMove(window, position)
        QTest.qWait(80)
        assert controller.inspection_tools.hover
        QTest.mouseClick(window, Qt.MouseButton.LeftButton, pos=position)
        QTest.qWait(60)
    rows = controller.session.command("measurement.list")
    assert len(rows) == 1 and abs(rows[0]["distance"] - 0.5) < 0.02, rows
    assert controller.session.history.cursor == cursor
    QTest.keyClick(window, Qt.Key.Key_Escape)
    assert not controller.inspection_tools.active


def pickability(controller):
    tools = controller.inspection_tools
    tools.toggle()
    for setting in ("hidden_categories", "unpickable_categories"):
        controller.run("workspace.update", {setting: ["geometry"]})
        QTest.qWait(50)
        tools.probe([0, -3, 0], [0, 1, 0], 0, False)
        assert not tools.hover
        controller.run("workspace.update", {setting: []})
        QTest.qWait(50)
        tools.probe([0, -3, 0], [0, 1, 0], 0, False)
        assert tools.hover
    tools.cancel()


def bookmarks(controller, window):
    click(window, "bookmarkName").setProperty("text", "Comparison front")
    click(window, "saveBookmark")
    saved = controller.session.workspace.bookmarks[0]
    find(window, "viewport").forceActiveFocus()
    QTest.keyClick(window, Qt.Key.Key_1)
    QTest.qWait(70)
    controller.inspection_tools.restoreBookmark(saved.id)
    QTest.qWait(100)
    observed = json.loads(window.inspectScene())
    assert observed["camera"] == list(saved.camera) and observed["orthographic"]
    assert window.grabWindow().save(str(OUTPUT / "ruler-bookmark.png"))


def export(controller, entity):
    path = OUTPUT / "measurements.afinspection.zip"
    controller.inspection_export.start(str(path))
    controller.run("scp.transform", dict(entity=entity, values=[1, 0, 0, 0, 0, 0, 1, 1, 1]))
    settle(controller)
    assert path.exists(), controller.session.scheduler.errors
    with ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
        (OUTPUT / "report.png").write_bytes(archive.read("image.png"))
    assert len(data["measurements"]) == 1 and not data["measurements"][0]["stale"]
    assert controller.session.command("measurement.list")[0]["stale"]


def bookmark_gesture(controller, window):
    entity = editable_body(controller)
    identity = select_point(controller, entity)
    before, cursor = position(controller, identity), controller.session.history.cursor
    pointer = begin_modal(controller, window, Qt.Key_G)
    QTest.mouseMove(window, pointer + QPoint(20, 15))
    QTest.qWait(60)
    restore_during_gesture(controller, window, identity)
    QTest.mouseMove(window, pointer + QPoint(35, 30))
    QTest.qWait(60)
    key(window, Qt.Key_Return)
    check_undo(controller, identity, before, cursor)


def editable_body(controller):
    root = controller.session.document.entities[0].id
    entity = controller.run("primitive.create", dict(kind="BODY", parent=root))
    settle(controller)
    controller.select(entity)
    controller.authoring.setEditing(True)
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, 3], True)
    QTest.qWait(120)
    return entity


def restore_during_gesture(controller, window, identity):
    changed, transaction = position(controller, identity), controller.session.history.before
    controller.inspection_tools.restoreBookmark(controller.session.workspace.bookmarks[0].id)
    QTest.qWait(100)
    np.testing.assert_allclose(position(controller, identity), changed, atol=1e-7)
    assert controller.session.history.before is transaction
    assert find(window, "modalTransform").property("active")


def run():
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        exercise(controller, engine.rootObjects()[0])
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


def exercise(controller, window):
    entity = fixture(controller)
    pickability(controller)
    ruler(controller, window)
    bookmarks(controller, window)
    export(controller, entity)
    bookmark_gesture(controller, window)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run()
    print(json.dumps(dict(inspection_acceptance=True)))
