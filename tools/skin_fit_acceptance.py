"""Background-only skin fitting controls, independent preview and geometry screenshots."""

import json
import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from skin_qualification_scene import setup
from ui_acceptance import click, find
from workbench_acceptance import activate, reveal

from anthroforge.desktop import app, runtime
from anthroforge.desktop.controller import Controller

OUTPUT = Path(os.environ.get("AF_SKIN_OUTPUT", "build/skin-040/ui")).resolve()


def settle(controller):
    controller.session.wait()
    controller.refresh()
    for _ in range(20):
        controller.process_tick()
        QTest.qWait(20)


def setup_view(controller, window):
    identity = setup(controller.session)
    controller.selection_view.select(controller.session.document.entities[0].id)
    settle(controller)
    controller.viewport_view.frameSelection()
    click(window, "shortcutsTab")
    controller.shortcut_panel.editor.select(identity)
    QTest.qWait(250)
    activate(window, "shortcutFitBones")
    QTest.qWait(150)
    assert find(window, "skinFitStart").isEnabled()
    assert window.grabWindow().save(str(OUTPUT / "fit-dialog.png"))
    return identity


def fit(controller, window):
    field = find(window, "skinFitMaximum")
    field.setProperty("canonicalValue", 0.2)
    activate(window, "skinFitStart")
    settle(controller)
    assert controller.session.document.skin.fits, controller.message
    item = controller.session.document.skin.fits[-1]
    click(window, "skinTab")
    controller.skin_panel.fits.select(item.id)
    reveal(window, "skinFits")
    controller.skin_panel.fits.preview(0.1)
    settle(controller)
    assert controller.skin_panel.fits.previewState["visible"]
    assert window.grabWindow().save(str(OUTPUT / "fit-preview.png"))


def diagnostics(controller, window):
    before = controller.session.document
    report = controller.session.command("skin.report")
    assert "solver" in report["final"]["report"]
    assert "intersections" in report["final"]["report"]
    reveal(window, "skinAchievedBudgets")
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / "skin-diagnostics.png"))
    assert controller.session.document is before


def exercise(application):
    controller, warnings = Controller(), []
    controller.timer.stop()
    engine = app.create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        scenarios(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        (OUTPUT / "fit-ui.json").write_text(json.dumps(dict(passed=True, warnings=warnings)))
    finally:
        controller.close()
        delete(engine)
        application.processEvents()


def scenarios(controller, window):
    QTest.qWait(200)
    setup_view(controller, window)
    fit(controller, window)
    diagnostics(controller, window)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    native = os.environ.get("AF_SKIN_BUILD")
    if native:
        runtime.build_directory = lambda: Path(native)
        app.build_directory = runtime.build_directory
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    application.setFont(QFont("Segoe UI"))
    with runtime.native_runtime():
        exercise(application)


if __name__ == "__main__":
    main()
