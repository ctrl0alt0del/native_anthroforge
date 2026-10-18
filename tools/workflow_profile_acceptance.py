"""Counterbalanced runtime recordings with the relationship inspector closed/open."""

import json
from pathlib import Path

import profiler_acceptance as acceptance
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import fixture

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.profiling import report

OUTPUT = Path("build/workflow-017/profiles").resolve()


def trials(controller, window):
    point, results = fixture(controller, window, 0.5), []
    for opened in (False, True, True, False):
        prepare(window, opened)
        for snap in (False, True):
            result = acceptance.trial(controller, window, point, snap, False)
            result["inspector_open"] = opened
            results.append(result)
            (OUTPUT / "acceptance.json").write_text(json.dumps(results, indent=2))
            print(json.dumps(dict(open=opened, snap=snap, path=result["path"])), flush=True)


def prepare(window, opened):
    panel = acceptance.find(window, "dependencyInspector")
    panel.setProperty("expanded", opened)
    inspector = acceptance.find(window, "inspector")
    QTest.qWait(100)
    inspector.property("contentItem").setProperty("contentY", panel.y() if opened else 0)
    QTest.qWait(100)


def run():
    profiler, controller, warnings = QtProfiler(), open_controller(None), []
    controller.capture_mode, controller.qt_profiler = True, profiler
    engine = create_engine(controller, warnings)
    try:
        trials(controller, engine.rootObjects()[0])
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        profiler.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    acceptance.OUTPUT = OUTPUT
    report.default_directory = lambda: OUTPUT
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
