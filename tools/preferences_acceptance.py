"""Actual Preferences QML, persistence and routed-fiber dispatch without desktop input."""

import json
import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from tissue_editor_acceptance import settle
from ui_acceptance import click, find

from anthroforge.application.preferences import PreferenceStore
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime
from tests.routed_surface_scene import create

OUTPUT = Path("build/preferences-023").resolve()


def backend(controller, key):
    item = controller.session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return controller.session.resources.paths[item.result.asset].diagnostics.backend


def choose(window, index, name="routingBackend"):
    combo = click(window, name)
    QTest.keyClick(window, Qt.Key.Key_Home)
    if index:
        QTest.keyClick(window, Qt.Key.Key_Down)
    QTest.keyClick(window, Qt.Key.Key_Return)
    QTest.qWait(100)
    assert combo.property("currentIndex") == index


def exercise(controller, window):
    objects = create(controller.session)
    controller.select(objects["fibers"][0])
    settle(controller)
    before, history = controller.session.document, controller.session.history.cursor
    assert QMetaObject.invokeMethod(find(window, "preferencesMenu"), "triggered")
    QTest.qWait(100)
    assert window.property("modalOpen")
    choose(window, 1)
    conversion_choice(controller, window)
    assert controller.session.document is before and controller.session.history.cursor == history
    assert backend(controller, objects["fibers"][0]) == "CUSTOM"
    assert window.grabWindow().save(str(OUTPUT / "preferences.png"))
    verify_dispatch(controller, window, objects)


def conversion_choice(controller, window):
    control = find(window, "routingConversionPoints")
    assert control.property("currentIndex") == 0
    choose(window, 1, "routingConversionPoints")
    assert controller.session.preferences.value.routing_conversion_points == "ALL_POINTS"
    assert (
        PreferenceStore(controller.session.preferences.path).value.routing_conversion_points
        == "ALL_POINTS"
    )
    choose(window, 0, "routingConversionPoints")
    assert controller.session.preferences.value.routing_conversion_points == "ENDPOINTS"


def verify_dispatch(controller, window, objects):
    assert QMetaObject.invokeMethod(find(window, "preferencesDialog"), "close", Qt.DirectConnection)
    controller.session.command("evaluate")
    settle(controller)
    assert all(backend(controller, key) == "PIQP" for key in objects["fibers"])
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    path = controller.session.preferences.path
    assert PreferenceStore(path).value.routing_backend == "PIQP"
    controller.newDocument()
    assert controller.session.preferences.value.routing_backend == "PIQP"
    report = dict(gui="offscreen", persisted=True, future_dispatch=True, fiber_backend="PIQP")
    (OUTPUT / "ui.json").write_text(json.dumps(report, indent=2))


def run():
    controller, warnings = Controller(), []
    controller.session.preferences = PreferenceStore(OUTPUT / "preferences.json")
    controller.session.preferences.update(routing_backend="CUSTOM")
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        QTest.qWait(350)
        exercise(controller, window)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run()
            print("Preferences UI and routed fiber dispatch passed offscreen.")
        finally:
            delete(app)


if __name__ == "__main__":
    main()
