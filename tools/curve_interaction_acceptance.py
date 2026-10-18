"""Real held-key and mouse gestures against the production desktop."""

import json
from pathlib import Path

import numpy as np
from primitive_acceptance import settle, source_curve
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QEvent, QMetaObject, QPointF, Qt
from PySide6.QtGui import QGuiApplication, QQuaternion, QVector3D
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/curve-interaction-review").resolve()
LEFT = Qt.MouseButton.LeftButton
SHIFT = Qt.KeyboardModifier.ShiftModifier
CTRL = Qt.KeyboardModifier.ControlModifier


def screen(window, world):
    viewport = find(window, "viewport")
    point = QMetaObject.invokeMethod(
        viewport, "projectPoint", Q_RETURN_ARG(QPointF), *(Q_ARG(float, float(v)) for v in world)
    )
    return viewport.mapToScene(point).toPoint()


def move(window, world):
    point = screen(window, world)
    QTest.mouseMove(window, point)
    QTest.qWait(70)
    return point


def capture(window, name):
    QTest.qWait(70)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def fixture(controller, window):
    root = controller.run("scp.empty", dict(name="Curve gesture fixture"))
    entity = controller.run("primitive.create", dict(kind="LOFT", parent=root))
    targets = [cube(controller, root, x, z) for x, z in ((-0.55, -0.6), (0.55, -0.3))]
    controller.run("scp.transform", dict(entity=entity, values=[0, 0, 0.3, 0, 0, 20, 1.2, 0.8, 1]))
    controller.select(entity)
    controller.authoring.setEditing(True)
    settle(controller)
    window.resize(1500, 950)
    controller.cameraRequested.emit([0, 0.2, 0, -90, 0, 0, 3], True)
    QTest.qWait(180)
    find(window, "viewport").forceActiveFocus()
    return entity, targets


def cube(controller, root, x, z):
    path = str(Path("examples/primitives/cube.obj").resolve())
    result = controller.run("import", dict(path=path, units=1, parent=root))
    settle(controller)
    entity = result["entity_id"]
    controller.run(
        "scp.transform", dict(entity=entity, values=[x, 0.7, z, 0, 0, 15, 0.5, 0.5, 0.5])
    )
    return entity


def insert_points(controller, window, entity):
    editor, cursor = controller.authoring, controller.session.history.cursor
    frame = controller.session.document.entity(entity).matrix
    point = move(window, controller.session.engine.world_point(frame, [-0.2, -0.15, 0]))
    QTest.keyPress(window, Qt.Key.Key_Shift)
    QTest.qWait(70)
    assert editor.interaction.preview, "Held Shift must show a preview before clicking."
    assert controller.session.history.cursor == cursor
    capture(window, "insertion-preview")
    QTest.mouseClick(window, LEFT, SHIFT, point)
    QTest.qWait(80)
    point = move(window, controller.session.engine.world_point(frame, [0.2, -0.15, 0]))
    QTest.mouseClick(window, LEFT, SHIFT, point)
    QTest.keyRelease(window, Qt.Key.Key_Shift)
    finish_insertions(controller, entity, cursor)


def finish_insertions(controller, entity, cursor):
    settle(controller)
    assert not controller.authoring.interaction.preview
    assert len(source_curve(controller, entity).points) == 4
    assert controller.session.history.cursor == cursor + 2
    controller.run("undo", {})
    assert len(source_curve(controller, entity).points) == 3
    controller.run("redo", {})
    settle(controller)


def point_row(editor, point):
    return next(
        row
        for row in editor.componentRows
        if row.get("point") == point and row["part"] == "position"
    )


def snap_drag(controller, window, entity, targets, preheld=False):
    editor = controller.authoring
    point = source_curve(controller, entity).points[1].id
    row = point_row(editor, point)
    cursor = controller.session.history.cursor
    start = move(window, row["world"])
    press_drag(window, start, preheld)
    check_target(controller, window, point, targets[0], [-0.55, 0.7, -0.35])
    check_target(controller, window, point, targets[1], [0.55, 0.7, -0.05])
    capture(window, "surface-snap")
    QTest.keyRelease(window, Qt.Key.Key_Control)
    assert not editor.interaction.snap
    finish_drag(controller, window, point, cursor, row["world"])


def press_drag(window, start, preheld):
    if preheld:
        QTest.keyPress(window, Qt.Key.Key_Control)
    QTest.mousePress(window, LEFT, CTRL if preheld else Qt.NoModifier, start)
    if not preheld:
        QTest.keyPress(window, Qt.Key.Key_Control)


def check_target(controller, window, point, target, position):
    move(window, position)
    hit = controller.authoring.interaction.snap
    assert hit.get("id") == target, hit
    actual = point_row(controller.authoring, point)["world"]
    np.testing.assert_allclose(actual, hit["point"], atol=1e-7)


def finish_drag(controller, window, point, cursor, before):
    end = move(window, [0.3, 0.4, 0])
    actual = point_row(controller.authoring, point)["world"]
    assert_in_view_plane(window, before, actual)
    QTest.mouseRelease(window, LEFT, pos=end)
    settle(controller)
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    np.testing.assert_allclose(point_row(controller.authoring, point)["world"], before, atol=1e-7)


def assert_in_view_plane(window, before, actual):
    camera = find(window, "viewport").property("cameraState").toVariant()
    direction = QQuaternion.fromEulerAngles(*camera[3:6]).rotatedVector(QVector3D(0, 0, -1))
    normal = [direction.x(), -direction.z(), direction.y()]
    assert abs(np.dot(np.subtract(actual, before), normal)) < 1e-6


def focus_rules(controller, window):
    move(window, [0, -0.1, 0.3])
    QTest.keyPress(window, Qt.Key.Key_Shift)
    QTest.qWait(40)
    assert controller.authoring.interaction.preview
    QGuiApplication.sendEvent(window, QEvent(QEvent.Type.WindowDeactivate))
    assert not controller.authoring.interaction.preview
    QTest.keyRelease(window, Qt.Key.Key_Shift)
    click(window, "outlinerSearch")
    QTest.keyPress(window, Qt.Key.Key_Shift)
    assert not controller.authoring.interaction.preview
    QTest.keyRelease(window, Qt.Key.Key_Shift)
    find(window, "viewport").forceActiveFocus()


def rebind_preview(controller, window):
    manager = find(window, "keyboardManager")
    bindings = manager.property("modifierBindings").toVariant()
    manager.setProperty("modifierBindings", dict(bindings, insertPoint=Qt.AltModifier.value))
    move(window, [0, -0.1, 0.3])
    QTest.keyPress(window, Qt.Key.Key_Shift)
    assert not controller.authoring.interaction.preview
    QTest.keyRelease(window, Qt.Key.Key_Shift)
    QTest.keyPress(window, Qt.Key.Key_Alt)
    QTest.qWait(40)
    assert controller.authoring.interaction.preview
    QTest.keyRelease(window, Qt.Key.Key_Alt)
    assert not controller.authoring.interaction.preview
    manager.setProperty("modifierBindings", bindings)


def perspective_drag(controller, window, entity, targets):
    controller.cameraRequested.emit([0, 0.2, 0, -55, 15, 0, 3], False)
    QTest.qWait(150)
    snap_drag(controller, window, entity, targets, True)
    capture(window, "perspective-colors")


def scope_and_exclusion(controller, window, entity, targets):
    from anthroforge.desktop.curve_interaction import surface_hit
    from anthroforge.desktop.scene_state import mesh_hits

    assert mesh_hits(controller, [0, 0, 5], [0, 0, -1])[0]["id"] == entity
    assert not surface_hit(controller, [0, 0, 5], [0, 0, -1])
    controller.run("workspace.create", dict(name="Edited part", members=[entity]))
    settle(controller)
    snap_drag(controller, window, entity, targets, True)


def gizmo_snap(controller, window, target):
    from usability_acceptance import geometry, offset, point

    g = geometry(window, "Move")
    start = point(window, offset(g["center"], g["axes"][1], 0.9))
    cursor = controller.session.history.cursor
    QTest.mousePress(window, LEFT, pos=start)
    assert find(window, "transformGizmo").property("dragging")
    QTest.keyPress(window, Qt.Key.Key_Control)
    end = move(window, [0.55, 0.7, 0])
    assert controller.authoring.interaction.snap.get("id") == target
    QTest.keyClick(window, Qt.Key.Key_Escape, CTRL)
    QTest.keyRelease(window, Qt.Key.Key_Control)
    QTest.mouseRelease(window, LEFT, pos=end)
    assert controller.session.history.cursor == cursor


def verify(controller, window):
    entity, targets = fixture(controller, window)
    insert_points(controller, window, entity)
    snap_drag(controller, window, entity, targets)
    focus_rules(controller, window)
    rebind_preview(controller, window)
    gizmo_snap(controller, window, targets[1])
    perspective_drag(controller, window, entity, targets)
    scope_and_exclusion(controller, window, entity, targets)
    capture(window, "curve-colors")
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    return acceptance_flags()


def acceptance_flags():
    return dict(
        repeated_insertion=True,
        surface_switching=True,
        modifier_release=True,
        one_drag_undo=True,
        focus_rules=True,
        rebound_modifier=True,
        both_projections=True,
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        result = verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        result["metrics"] = controller.session.scheduler.metrics.report()
        (OUTPUT / "acceptance.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
