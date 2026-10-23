"""Background-only shortcut inspection, layout, native overlays and observational purity."""

import json
import sys
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shortcuts_editor_acceptance import create_engine, prepare, settle
from shortcuts_scene_acceptance import frames, scene
from ui_acceptance import find

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/shortcut-inspection-review")


def inspect_editor(controller, warnings):
    curve, driver, _ = prepare(controller)
    engine = create_engine(controller, curve, warnings)
    view = controller.shortcut_panel.editor.inspection
    view.activate(True)
    window = engine.rootObjects()[0]
    for title in ("Formula values", "Attachment effects", "Update details"):
        button = find(window, title + "Toggle")
        button.clicked.emit()
    QTest.qWait(100)
    assert view.effects.rowCount() > 0 and view.value["formulas"]
    layout_during_edit(controller, window, driver)
    assert window.grabWindow().save(str(OUTPUT / "inspection-editor.png"))
    window.close()


def layout_during_edit(controller, window, driver):
    field = find(window, "driverValue")
    before = (field.x(), field.y(), field.width(), field.height())
    controller.session.begin()
    for value in (0.4, 0.5, 0.6):
        controller.run("driver.value", dict(driver=driver, value=value))
        settle(controller)
        assert (field.x(), field.y(), field.width(), field.height()) == before
    controller.session.cancel()
    settle(controller)
    assert controller.shortcut_panel.editor.inspection.value["progress"]["state"] == "cancelled"


def inspect_scene(controller, warnings, application):
    renderer = Offscreen(controller, warnings)
    try:
        curve, _ = scene(controller)
        image = frames(controller, renderer, application)
        assert image.save(str(OUTPUT / "effects-off.png"))
        variable = controller.session.document.object(curve).engine_settings.variables[0].id
        ref = dict(target=curve, path=["engine_settings", "variables", "@" + variable, "value"])
        key = controller.run("shortcut.expose", dict(reference=ref))
        overlays(controller, renderer, application, key)
    finally:
        renderer.close()


def overlays(controller, renderer, application, key):
    editor = controller.shortcut_panel.editor
    editor.select(key)
    editor.inspection.activate(True)
    before, cursor, selected = identity(controller)
    editor.inspection.showEffects(True)
    image = frames(controller, renderer, application)
    capture_effects(controller, renderer, image)
    assert controller.session.document is before and controller.session.history.cursor == cursor
    assert controller.selection == selected
    editor.inspection.showEffects(False)
    assert not editor.inspection.snapshot()


def identity(controller):
    return controller.session.document, controller.session.history.cursor, controller.selection


def capture_effects(controller, renderer, image):
    editor = controller.shortcut_panel.editor
    assert image.save(str(OUTPUT / "effects-on.png"))
    assert editor.inspection.snapshot()["shown"]
    assert find(renderer.window, "shortcutEffectsOutline").property("visible")
    (OUTPUT / "effects-state.json").write_text(json.dumps(editor.inspection.snapshot()))
    find(renderer.window, "selectionOutline").setProperty("visible", False)
    image = renderer.frame()
    assert image.save(str(OUTPUT / "effects-without-selection-mask.png"))


def run(mode, application):
    controller, warnings = Controller(), []
    try:
        if mode == "editor":
            inspect_editor(controller, warnings)
        else:
            inspect_scene(controller, warnings, application)
        assert not warnings, warnings
        (OUTPUT / (mode + ".json")).write_text(json.dumps(dict(passed=True, interactive=False)))
    finally:
        controller.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    application.setFont(QFont("Segoe UI", 10))
    with native_runtime():
        run(sys.argv[1], application)
