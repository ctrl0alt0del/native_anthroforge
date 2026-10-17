"""Exercise camera bookmarks through production keyboard, button and menu actions."""

import json
from pathlib import Path

import numpy as np
from curve_interaction_acceptance import fixture
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from ui_acceptance import click, find
from view_gesture_acceptance import key, select_point, value

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/camera-restore-review").resolve()


def snapshot(window):
    viewport = find(window, "viewport")
    return dict(
        values=value(viewport, "cameraState") + [viewport.property("distance")],
        name=viewport.property("viewName"),
    )


def assert_camera(window, expected):
    actual = snapshot(window)
    np.testing.assert_allclose(actual["values"], expected["values"], atol=1e-7)
    assert actual["name"] == expected["name"]


def capture(window, name):
    QTest.qWait(80)
    assert window.grabWindow().save(str(OUTPUT / f"{name}.png"))


def restore_cycle(controller, window, orthographic):
    controller.cameraRequested.emit([0.15, 0.2, 0.1, -55, 15, 7, 3.5], orthographic)
    QTest.qWait(80)
    original, cursor = snapshot(window), controller.session.history.cursor
    key(window, Qt.Key_4)
    assert_camera(window, original)
    capture(window, f"original-{orthographic}")
    mixed_navigation(window)
    capture(window, f"temporary-{orthographic}")
    key(window, Qt.Key_4)
    assert_camera(window, original)
    capture(window, f"restored-{orthographic}")
    key(window, Qt.Key_4)
    assert_camera(window, original)
    assert controller.session.history.cursor == cursor


def mixed_navigation(window):
    key(window, Qt.Key_1)
    click(window, "viewY")
    key(window, Qt.Key_3)
    click(window, "viewZ")
    assert find(window, "restoreView").property("enabled")
    key(window, Qt.Key_5)
    find(window, "viewport").setProperty("distance", 2.5)


def restore_controls(window):
    viewport = find(window, "viewport")
    viewport.setProperty("distance", 4.25)
    viewport.setProperty("viewName", "Custom view")
    original = snapshot(window)
    click(window, "viewX")
    click(window, "restoreView")
    assert_camera(window, original)
    click(window, "viewZ")
    assert QMetaObject.invokeMethod(find(window, "restoreViewMenu"), "triggered")
    assert_camera(window, original)
    assert not viewport.property("canRestoreView")
    assert not find(window, "restoreView").property("enabled")


def focus_and_binding_checks(window):
    key(window, Qt.Key_1)
    before = snapshot(window)
    search = click(window, "outlinerSearch")
    key(window, Qt.Key_4)
    assert search.property("text") == "4"
    assert_camera(window, before)
    search.setProperty("text", "")
    find(window, "viewport").forceActiveFocus()
    binding_checks(window)


def binding_checks(window):
    manager, before = find(window, "keyboardManager"), snapshot(window)
    bindings = value(manager, "bindings")
    changed = [dict(row, key="8") if row["command"] == "restoreView" else row for row in bindings]
    manager.setProperty("bindings", changed)
    QTest.qWait(80)
    key(window, Qt.Key_4)
    assert_camera(window, before)
    assert find(window, "restoreView").property("text") == "Restore · 8"
    key(window, Qt.Key_8)
    assert not find(window, "viewport").property("canRestoreView")
    manager.setProperty("bindings", bindings)


def workspace_checks(controller, window, entity):
    key(window, Qt.Key_2)
    controller.run("workspace.create", dict(name="Camera scope", members=[entity]))
    QTest.qWait(100)
    assert not find(window, "viewport").property("canRestoreView")
    original = snapshot(window)
    key(window, Qt.Key_4)
    assert_camera(window, original)
    key(window, Qt.Key_3)
    controller.run("workspace.select", dict(index=0))
    QTest.qWait(100)
    assert not find(window, "viewport").property("canRestoreView")


def persistence_checks(controller, window):
    original, cursor = snapshot(window), controller.session.history.cursor
    controller.capture_mode = False
    key(window, Qt.Key_1)
    QTest.qWait(300)
    key(window, Qt.Key_4)
    QTest.qWait(300)
    p = original["values"]
    np.testing.assert_allclose(
        controller.session.workspace.camera, [p[0], -p[2], p[1], *p[3:6], p[7]]
    )
    assert controller.session.workspace.orthographic == p[6]
    assert controller.session.history.cursor == cursor
    controller.capture_mode = True


def verify(controller, window):
    entity, _ = fixture(controller, window)
    select_point(controller, entity)
    for orthographic in (False, True):
        restore_cycle(controller, window, orthographic)
    restore_controls(window)
    focus_and_binding_checks(window)
    workspace_checks(controller, window, entity)
    persistence_checks(controller, window)
    return dict(
        camera_restore=True, keyboard_buttons_menu=True, focus_rebinding=True, workspace=True
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        result = verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        (OUTPUT / "acceptance.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
