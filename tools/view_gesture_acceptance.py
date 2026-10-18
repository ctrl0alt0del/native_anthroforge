"""Real keyboard, pointer and wheel acceptance for view changes during edits."""

import json
from pathlib import Path

import numpy as np
from curve_interaction_acceptance import CTRL, LEFT, fixture, move, point_row, screen
from primitive_acceptance import settle
from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QGuiApplication, QKeyEvent, QQuaternion, QVector3D, QWheelEvent
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import click, find
from usability_acceptance import geometry, offset, point

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/view-gesture-review").resolve()


def value(item, name):
    result = item.property(name)
    return result.toVariant() if hasattr(result, "toVariant") else result


def key(window, code, modifiers=Qt.NoModifier):
    if modifiers:
        # Preserve physically held modifiers; QTest.keyClick synthesizes their release.
        for kind in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            QGuiApplication.sendEvent(window, QKeyEvent(kind, code, modifiers))
    else:
        QTest.keyClick(window, code)
    QTest.qWait(65)


def select_point(controller, entity):
    editor = controller.authoring
    point_id = controller.session.document.entity(entity).primitive.curves[0].points[0].id
    row = point_row(editor, point_id)
    editor.selectComponent(row["key"], False)
    return point_id


def position(controller, point_id):
    return np.array(point_row(controller.authoring, point_id)["world"])


def centered(window, world):
    viewport = find(window, "viewport")
    center = viewport.mapToScene(QPointF(viewport.width() / 2, viewport.height() / 2)).toPoint()
    assert (screen(window, world) - center).manhattanLength() <= 2


def view_checks(controller, window, point_id):
    viewport = find(window, "viewport")
    controller.cameraRequested.emit([0, 0.2, 0, -55, 15, 0, 3], False)
    QTest.qWait(90)
    pivot = position(controller, point_id)
    zoom = apparent_zoom(window, pivot)
    for code, rotation in ((Qt.Key_1, [0, 90, 0]), (Qt.Key_2, [0, 0, 0]), (Qt.Key_3, [-90, 0, 0])):
        key(window, code)
        assert value(viewport, "cameraState")[3:6] == rotation
        assert viewport.property("orthographic")
        centered(window, pivot)
        assert abs(apparent_zoom(window, pivot) - zoom) <= 2
        previous = viewport.property("distance")
        key(window, code)
        np.testing.assert_allclose(viewport.property("distance"), previous, rtol=1e-12)


def apparent_zoom(window, pivot):
    camera = value(find(window, "viewport"), "cameraState")
    right = QQuaternion.fromEulerAngles(*camera[3:6]).rotatedVector(QVector3D(1, 0, 0))
    world = np.array(pivot) + 0.2 * np.array([right.x(), -right.z(), right.y()])
    return (screen(window, world) - screen(window, pivot)).manhattanLength()


def begin_modal(controller, window, code):
    viewport = find(window, "viewport")
    viewport.forceActiveFocus()
    start = viewport.mapToScene(QPointF(viewport.width() * 0.7, viewport.height() * 0.45)).toPoint()
    QTest.mouseMove(window, start)
    key(window, code)
    assert find(window, "modalTransform").property("active")
    assert controller.session.history.before is not None
    return start


def modal_move(controller, window, point_id):
    before, cursor = position(controller, point_id), controller.session.history.cursor
    pointer = begin_modal(controller, window, Qt.Key_G)
    for code, axis in ((Qt.Key_1, 0), (Qt.Key_2, 1), (Qt.Key_3, 2)):
        pointer += QPoint(24, -17)
        modal_step(controller, window, point_id, code, axis, pointer)
        assert controller.session.history.cursor == cursor
    restore_edit(controller, window, lambda: position(controller, point_id))
    assert window.grabWindow().save(str(OUTPUT / "modal-axis-edit.png"))
    key(window, Qt.Key_Return)
    check_undo(controller, point_id, before, cursor)


def modal_step(controller, window, point_id, code, axis, pointer):
    old = position(controller, point_id)
    key(window, code)
    np.testing.assert_allclose(position(controller, point_id), old, atol=1e-7)
    QTest.mouseMove(window, pointer)
    QTest.qWait(45)
    delta = position(controller, point_id) - old
    assert abs(delta[axis]) < 1e-7 and np.linalg.norm(delta) > 0.01, (axis, delta)


def check_undo(controller, point_id, before, cursor):
    settle(controller)
    assert controller.session.history.before is None
    assert controller.session.history.cursor == cursor + 1, (
        cursor,
        controller.session.history.cursor,
        before,
        position(controller, point_id),
    )
    controller.run("undo", {})
    settle(controller)
    np.testing.assert_allclose(position(controller, point_id), before, atol=1e-7)


def direct_views(controller, window, point_id):
    key(window, Qt.Key_3)
    before, cursor = position(controller, point_id), controller.session.history.cursor
    pointer = move(window, before)
    QTest.mousePress(window, LEFT, pos=pointer)
    pointer += QPoint(30, 20)
    QTest.mouseMove(window, pointer)
    QTest.qWait(60)
    switch_and_restore(controller, window, lambda: position(controller, point_id))
    assert find(window, "curveEditor").property("dragging")
    QTest.mouseMove(window, pointer + QPoint(20, -20))
    QTest.mouseRelease(window, LEFT, pos=pointer + QPoint(20, -20))
    check_undo(controller, point_id, before, cursor)


def wheel(window, pointer, notches, buttons=LEFT):
    event = QWheelEvent(
        QPointF(pointer),
        QPointF(window.mapToGlobal(pointer)),
        QPoint(),
        QPoint(0, notches * 120),
        buttons,
        CTRL,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QGuiApplication.sendEvent(window, event)
    QTest.qWait(50)


def assert_offset(controller, point_id, sign):
    hit, offset = controller.authoring.interaction.snap, controller.authoring.interaction.offset
    assert offset * sign > 0
    expected = np.array(hit["surface"]) + offset * np.array(hit["normal"])
    np.testing.assert_allclose(position(controller, point_id), expected, atol=1e-7)


def offset_checks(controller, window, point_id, targets, modal=False):
    controller.cameraRequested.emit([0, 0.2, 0, -90, 0, 0, 3], True)
    QTest.qWait(80)
    before, cursor = position(controller, point_id), controller.session.history.cursor
    pointer = move(window, before)
    if modal:
        begin_modal(controller, window, Qt.Key_G)
    else:
        QTest.mousePress(window, LEFT, pos=pointer)
    QTest.keyPress(window, Qt.Key_Control)
    pointer = move(window, [-0.55, 0.7, -0.35])
    assert controller.authoring.interaction.snap["id"] == targets[0]
    offset_steps(controller, window, point_id, pointer, targets)
    snap_view_switch(controller, window, point_id)
    finish_offset(controller, window, point_id, before, cursor, modal)


def snap_view_switch(controller, window, point_id):
    before, offset = position(controller, point_id), controller.authoring.interaction.offset
    for code, angles in ((Qt.Key_1, [0, 90, 0]), (Qt.Key_3, [-90, 0, 0])):
        key(window, code, CTRL)
        assert value(find(window, "viewport"), "cameraState")[3:6] == angles
        np.testing.assert_allclose(position(controller, point_id), before, atol=1e-7)
        assert controller.authoring.interaction.offset == offset
        assert controller.session.history.before is not None
    restore_edit(controller, window, lambda: position(controller, point_id), CTRL)
    assert controller.authoring.interaction.offset == offset


def offset_steps(controller, window, point_id, pointer, targets):
    viewport, interaction = find(window, "viewport"), controller.authoring.interaction
    distance = viewport.property("distance")
    wheel(window, pointer, 2)
    assert_offset(controller, point_id, 1)
    assert viewport.property("distance") == distance
    pointer = move(window, [0.55, 0.7, -0.05])
    assert interaction.snap["id"] == targets[1]
    assert_offset(controller, point_id, 1)
    assert window.grabWindow().save(str(OUTPUT / "snap-offset.png"))
    reset_offset(controller, window, point_id, pointer)
    wheel(window, pointer, -1)
    assert_offset(controller, point_id, -1)


def reset_offset(controller, window, point_id, pointer):
    interaction = controller.authoring.interaction
    QTest.mouseClick(window, Qt.MiddleButton, CTRL, pointer)
    assert interaction.offset == 0 and controller.session.history.before is not None
    np.testing.assert_allclose(
        position(controller, point_id), interaction.snap["surface"], atol=1e-7
    )


def finish_offset(controller, window, point_id, before, cursor, modal):
    QTest.keyRelease(window, Qt.Key_Control)
    assert controller.authoring.interaction.offset == 0
    assert not controller.authoring.interaction.snap
    if modal:
        key(window, Qt.Key_Return)
    else:
        QTest.mouseRelease(window, LEFT, pos=screen(window, [0.55, 0.7, -0.05]))
    check_undo(controller, point_id, before, cursor)


def object_transforms(controller, window):
    controller.authoring.setEditing(False)
    for code in (Qt.Key_R, Qt.Key_S):
        object_gesture(controller, window, code)
    object_confirmation(controller, window)


def object_confirmation(controller, window):
    before, cursor = current_matrix(controller), controller.session.history.cursor
    pointer = begin_modal(controller, window, Qt.Key_G)
    QTest.mouseMove(window, pointer + QPoint(20, 15))
    key(window, Qt.Key_S)
    QTest.mouseMove(window, pointer + QPoint(40, 30))
    QTest.mouseClick(window, LEFT, pos=pointer + QPoint(40, 30))
    settle(controller)
    assert controller.session.history.before is None
    assert controller.session.history.cursor == cursor + 1
    assert current_matrix(controller) != before
    controller.run("undo", {})
    np.testing.assert_allclose(current_matrix(controller), before)


def object_gesture(controller, window, code):
    before = current_matrix(controller)
    pointer = begin_modal(controller, window, code)
    QTest.mouseMove(window, pointer + QPoint(35, 40))
    QTest.qWait(60)
    changed = current_matrix(controller)
    assert changed != before
    key(window, Qt.Key_2)
    np.testing.assert_allclose(current_matrix(controller), changed)
    restore_edit(controller, window, lambda: current_matrix(controller))
    QTest.mouseMove(window, pointer + QPoint(50, 60))
    QTest.qWait(50)
    assert current_matrix(controller) != changed
    QTest.mouseClick(window, Qt.RightButton, pos=pointer + QPoint(50, 60))
    np.testing.assert_allclose(current_matrix(controller), before)


def current_matrix(controller):
    return controller.session.document.entity(controller.selection).matrix


def gizmo_view(controller, window, point_id):
    key(window, Qt.Key_3)
    g = geometry(window, "Move")
    pointer = point(window, offset(g["center"], g["axes"][1], 0.9))
    QTest.mousePress(window, LEFT, pos=pointer)
    assert find(window, "transformGizmo").property("dragging")
    QTest.mouseMove(window, pointer + QPoint(20, 15))
    QTest.qWait(50)
    before = position(controller, point_id)
    switch_and_restore(controller, window, lambda: position(controller, point_id))
    QTest.mouseMove(window, pointer + QPoint(35, 30))
    QTest.qWait(50)
    assert np.linalg.norm(position(controller, point_id) - before) > 0.01
    key(window, Qt.Key_Escape)
    QTest.mouseRelease(window, LEFT, pos=pointer + QPoint(35, 30))


def focus_checks(controller, window):
    click(window, "outlinerSearch")
    for code in (Qt.Key_1, Qt.Key_4, Qt.Key_G, Qt.Key_R, Qt.Key_S):
        key(window, code)
    assert not find(window, "modalTransform").property("active")
    find(window, "outlinerSearch").setProperty("text", "")
    find(window, "viewport").forceActiveFocus()


def switch_and_restore(controller, window, read):
    before = read()
    key(window, Qt.Key_1)
    np.testing.assert_allclose(read(), before, atol=1e-7)
    restore_edit(controller, window, read)


def restore_edit(controller, window, read, modifiers=Qt.NoModifier):
    before, transaction = read(), controller.session.history.before
    key(window, Qt.Key_4, modifiers)
    np.testing.assert_allclose(read(), before, atol=1e-7)
    assert find(window, "viewport").property("transforming")
    assert not find(window, "viewport").property("canRestoreView")
    assert controller.session.history.before is transaction


def verify(controller, window):
    entity, targets = fixture(controller, window)
    point_id = select_point(controller, entity)
    view_checks(controller, window, point_id)
    modal_move(controller, window, point_id)
    direct_views(controller, window, point_id)
    gizmo_view(controller, window, point_id)
    offset_checks(controller, window, point_id, targets)
    offset_checks(controller, window, point_id, targets, True)
    object_transforms(controller, window)
    focus_checks(controller, window)
    assert window.grabWindow().save(str(OUTPUT / "axis-editing.png"))
    return dict(axis_views=True, modal_transforms=True, continuous_undo=True, surface_offset=True)


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
