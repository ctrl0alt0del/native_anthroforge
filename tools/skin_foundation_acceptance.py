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

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/skin-040/ui").resolve()


def edit(window):
    field = find(window, "skin_gap_limit_ratioValue")
    click(window, field.objectName())
    QTest.keyClick(window, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
    for character in "0.75":
        QTest.keyClick(window, Qt.Key(ord(character)))
    QTest.keyClick(window, Qt.Key.Key_Return)
    QTest.qWait(100)


def navigation(controller, window):
    before = controller.session.document
    for name in ("shapeTab", "shortcutsTab", "inspectTab", "skinTab"):
        click(window, name)
        QTest.qWait(30)
    assert controller.session.document is before
    assert find(window, "skinPane").isVisible()
    edit(window)
    assert controller.session.document.skin.envelope_settings.gap_limit_ratio == 0.0075
    controller.run("undo", {})
    assert controller.session.document.skin == before.skin
    window.resize(1050, 680)
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / "skin-settings.png"))


def exercise(application):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        assert engine.rootObjects(), warnings
        window = engine.rootObjects()[0]
        QTest.qWait(100)
        navigation(controller, window)
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
    print("Skin settings, vertical tabs and undo passed offscreen; geometry not tested.")


if __name__ == "__main__":
    main()
