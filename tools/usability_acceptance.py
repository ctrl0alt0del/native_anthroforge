"""0.1.3 acceptance through real Qt input, geometry presentation and shared commands."""

import json
import sys
from pathlib import Path

import numpy as np
from gui_acceptance import wait_until
from primitive_acceptance import settle
from PySide6.QtCore import QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime
from anthroforge.desktop.transform_delta import object_values

OUTPUT = Path("build/usability-review").resolve()


def screenshot(window, name):
    QTest.qWait(120)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def geometry(window, mode):
    click(window, "tool" + mode)
    QTest.qWait(80)
    item = find(window, "transformGizmo")
    value = item.property("geometry")
    return unpack(value.toVariant() if hasattr(value, "toVariant") else value)


def unpack(value):
    if isinstance(value, QPointF):
        return dict(x=value.x(), y=value.y())
    if isinstance(value, dict):
        return {k: unpack(v) for k, v in value.items()}
    if isinstance(value, list):
        return [unpack(v) for v in value]
    return value


def point(window, value):
    return find(window, "viewport").mapToScene(QPointF(value["x"], value["y"])).toPoint()


def offset(center, vector, amount):
    return {k: center[k] + vector[k] * amount for k in ("x", "y")}


def gesture(window, start, end, cancel=False):
    QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=point(window, start))
    assert find(window, "transformGizmo").property("dragging")
    for step in range(1, 9):
        value = {k: start[k] + (end[k] - start[k]) * step / 8 for k in ("x", "y")}
        QTest.mouseMove(window, point(window, value), 16)
        QTest.qWait(16)
    if cancel:
        QTest.keyClick(window, Qt.Key.Key_Escape)
    QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=point(window, end))
    QTest.qWait(100)


def check_delta(controller, before, delta):
    expected = object_values(
        controller.session.engine, controller.session.engine.decompose(before), delta
    )
    actual = controller.session.document.entity(controller.selection).matrix
    assert np.allclose(actual, controller.session.engine.transform(expected), atol=0.025), (
        actual,
        expected,
    )


def undo_check(controller, before, cursor):
    settle(controller)
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    assert np.allclose(controller.session.document.entity(controller.selection).matrix, before)


def rotate_check(controller, window, name="rotate"):
    g = geometry(window, "Rotate")
    before = controller.session.document.entity(controller.selection).matrix
    cursor = controller.session.history.cursor
    screenshot(window, name)
    gesture(window, g["rings"][2][13], g["rings"][2][25])
    check_delta(controller, before, [0, 0, 0, 0, 0, 45, 1, 1, 1])
    undo_check(controller, before, cursor)


def scale_check(controller, window, uniform=False):
    g = geometry(window, "Scale")
    before = controller.session.document.entity(controller.selection).matrix
    cursor = controller.session.history.cursor
    start = g["center"] if uniform else offset(g["center"], g["axes"][0], 0.85)
    end = offset(start, {"x": 40, "y": -20}, 1) if uniform else offset(start, g["axes"][0], 0.5)
    gesture(window, start, end)
    check_delta(
        controller, before, [0, 0, 0, 0, 0, 0, 1.5, 1.5 if uniform else 1, 1.5 if uniform else 1]
    )
    screenshot(window, "scale-uniform" if uniform else "scale-axis")
    undo_check(controller, before, cursor)


def move_plane_check(controller, window):
    g = geometry(window, "Move")
    before = controller.session.document.entity(controller.selection).matrix
    cursor = controller.session.history.cursor
    start = offset(offset(g["center"], g["axes"][0], 0.35), g["axes"][1], 0.35)
    end = offset(offset(start, g["axes"][0], 0.2), g["axes"][1], 0.1)
    gesture(window, start, end)
    check_delta(controller, before, [g["size"] * 0.2, g["size"] * 0.1, 0, 0, 0, 0, 1, 1, 1])
    screenshot(window, "move-plane")
    undo_check(controller, before, cursor)


def cancel_check(controller, window):
    g = geometry(window, "Move")
    before = controller.session.document.entity(controller.selection).matrix
    cursor = controller.session.history.cursor
    start = offset(g["center"], g["axes"][0], 0.85)
    gesture(window, start, offset(start, g["axes"][0], 0.4), cancel=True)
    settle(controller)
    assert np.allclose(controller.session.document.entity(controller.selection).matrix, before)
    assert controller.session.history.cursor == cursor


def free_move_check(controller, window):
    g = geometry(window, "Move")
    before = controller.session.document.entity(controller.selection).matrix
    cursor = controller.session.history.cursor
    gesture(window, g["center"], offset(g["center"], {"x": 45, "y": -25}, 1))
    assert not np.allclose(controller.session.document.entity(controller.selection).matrix, before)
    undo_check(controller, before, cursor)


def text_safe_delete(controller, window):
    search = click(window, "outlinerSearch")
    search.setProperty("text", "abc")
    QTest.keyClick(window, Qt.Key.Key_Home)
    QTest.keyClick(window, Qt.Key.Key_Delete)
    assert search.property("text") == "bc"
    assert not find(window, "deleteDialog").property("visible")
    search.setProperty("text", "")
    find(window, "viewport").forceActiveFocus()


def root_delete(controller, window):
    root = controller.selection
    before = {e.id: e.matrix for e in controller.session.document.entities if e.id != root}
    QTest.keyClick(window, Qt.Key.Key_Delete)
    dialog = find(window, "deleteDialog")
    assert dialog.property("visible") and "empty grouping root" in dialog.property("explanation")
    tool = window.property("activeTool")
    QTest.keyClick(window, Qt.Key.Key_E)
    assert window.property("activeTool") == tool
    screenshot(window, "delete-root")
    QMetaObject.invokeMethod(dialog, "accept")
    settle(controller)
    verify_root_deleted(controller, root, before)


def verify_root_deleted(controller, root, before):
    entities = controller.session.document.entities
    replacement = next(e for e in entities if not e.parent)
    assert replacement.id != root and replacement.primitive is None
    assert all(
        np.allclose(controller.session.document.entity(k).matrix, v) for k, v in before.items()
    )
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.entity(root)
    controller.select(root)


def tree_delete(controller, window):
    child = next(e for e in controller.session.document.entities if e.parent)
    click(window, "delete_" + child.id)
    dialog = find(window, "deleteDialog")
    assert not dialog.property("visible")
    settle(controller)
    assert all(e.id != child.id for e in controller.session.document.entities)
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.entity(child.id)


def curve_presentation(controller, window):
    controller.run(
        "workspace.update", dict(hidden=[e.id for e in controller.session.document.entities])
    )
    controller.authoring.create("BODY", "CAPSULE")
    settle(controller)
    controller.frameSelection()
    click(window, "toolMove")
    QTest.keyClick(window, Qt.Key.Key_1)
    surface = find(window, "surface_" + controller.selection + "_0")
    check_transparency(controller, window, surface)


def check_transparency(controller, window, surface):
    assert abs(surface.property("opacity") - 0.35) < 1e-6
    before = controller.session.document
    screenshot(window, "curve-edit-transparent")
    controller.authoring.setEditing(False)
    QTest.qWait(100)
    assert surface.property("opacity") == 1
    assert controller.session.document == before
    screenshot(window, "body-outline")


def gizmo_checks(controller, window):
    rotate_check(controller, window)
    scale_check(controller, window)
    scale_check(controller, window, uniform=True)
    move_plane_check(controller, window)
    free_move_check(controller, window)
    cancel_check(controller, window)
    drag_context_check(controller, window)
    controller.cameraRequested.emit([0, 0, 0, -25, 30, 0, 2.5], False)
    QTest.qWait(120)
    rotate_check(controller, window, "rotate-perspective")


def drag_context_check(controller, window):
    g = geometry(window, "Move")
    start = point(window, offset(g["center"], g["axes"][0], 0.85))
    QTest.mousePress(window, Qt.MouseButton.LeftButton, pos=start)
    QTest.keyClick(window, Qt.Key.Key_E)
    QTest.keyClick(window, Qt.Key.Key_Delete)
    assert window.property("activeTool") == "Move"
    assert not find(window, "deleteDialog").property("visible")
    QTest.keyClick(window, Qt.Key.Key_Escape)
    QTest.mouseRelease(window, Qt.MouseButton.LeftButton, pos=start)
    assert controller.session.history.before is None


def verify(controller, window):
    wait_until(lambda: not controller.render_model.pending)
    click(window, "toolMove")
    QTest.keyClick(window, Qt.Key.Key_7)
    gizmo_checks(controller, window)
    text_safe_delete(controller, window)
    root_delete(controller, window)
    tree_delete(controller, window)
    curve_presentation(controller, window)


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = fixture(), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, True)
    try:
        QTest.qWait(800)
        result = verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        write_report(controller, warnings, result)
    finally:
        controller.close()


def fixture():
    controller = open_controller(None)
    path = str(Path("examples/primitives/cube.obj").resolve())
    root = controller.run("import", dict(path=path, units=1.0))["entity_id"]
    settle(controller)
    child = controller.run("import", dict(path=path, units=1.0, parent=root))["entity_id"]
    settle(controller)
    controller.run("scp.transform", dict(entity=child, values=[1, 0, 0, 0, 0, 0, 0.2, 0.2, 0.2]))
    controller.run("scp.transform", dict(entity=root, values=[0, 0, 0, 0, 0, 25, 1, 1, 1]))
    settle(controller)
    controller.select(root)
    return controller


def write_report(controller, warnings, result):
    report = dict(
        passed=True,
        warnings=warnings,
        result=result,
        metrics=controller.session.scheduler.metrics.report(),
    )
    (OUTPUT / ("render.json" if "--render" in sys.argv else "acceptance.json")).write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report))


if __name__ == "__main__":
    if "--render" in sys.argv:
        from usability_render_checks import verify

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
