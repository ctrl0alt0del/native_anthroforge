"""Offscreen skin settings/navigation checks; does not claim skin geometry acceptance."""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.application import skin_evaluation
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/skin-040/ui").resolve()


def edit_field(window, name, text):
    field = find(window, name + "Value")
    click(window, field.objectName())
    QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
    for character in text:
        QTest.keyClick(window, Qt.Key(ord(character)))
    QTest.keyClick(window, Qt.Key.Key_Return)
    QTest.qWait(100)


def integer_settings(controller, window):
    window.resize(1050, 1300)
    QTest.qWait(100)
    edit_field(window, "skinQuadCount", "9000")
    assert controller.session.document.skin.topology_settings.target_quads == 9000
    edit_field(window, "skinProxyResolution", "32")
    assert controller.session.document.skin.deformation_settings.proxy_resolution == 32
    controller.run("undo", {})
    controller.run("undo", {})


def navigation(controller, window):
    before = controller.session.document
    for name in ("shapeTab", "shortcutsTab", "inspectTab", "skinTab"):
        click(window, name)
        QTest.qWait(30)
    assert controller.session.document is before
    assert find(window, "skinPane").isVisible()
    edit_field(window, "skin_gap_limit_ratio", "0.75")
    assert controller.session.document.skin.envelope_settings.gap_limit_ratio == 0.0075
    controller.run("undo", {})
    assert controller.session.document.skin == before.skin
    integer_settings(controller, window)
    window.resize(1050, 680)
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / "skin-settings.png"))


def envelope(controller, window):
    skin_evaluation.TARGET_RESOLUTION = 24
    controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1)
    )
    controller.session.wait()
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    click(window, "skinBuildEnvelope")
    controller.session.wait()
    controller.refresh()
    QTest.qWait(500)
    verify_skin_display(controller, window)


def verify_skin_display(controller, window):
    stage = controller.session.document.skin.envelope
    assert stage.asset, controller.session.scheduler.errors
    assert any(row["geometry_asset"] == stage.asset for row in controller.render_model.rows)
    assert window.grabWindow().save(str(OUTPUT / "skin-envelope.png"))
    controller.run("workspace.update", dict(skin_display="NONE"))
    QTest.qWait(100)
    assert not any(row["geometry_asset"] == stage.asset for row in controller.render_model.rows)
    controller.run("workspace.update", dict(skin_display="AUTO"))
    QTest.qWait(100)
    assert any(row["geometry_asset"] == stage.asset for row in controller.render_model.rows)


def exercise(application):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        QTest.qWait(100)
        navigation(controller, window)
        envelope(controller, window)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        application.processEvents()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "state/preferences.json")
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        application = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI"))
        exercise(application)
    print("Skin UI checks passed offscreen; GPU pixels checked separately.")


if __name__ == "__main__":
    main()
