"""Serial normal/snapped drag recordings with Issues hidden/shown, using runtime profiling."""

import json
from pathlib import Path
from zipfile import ZipFile

import profiler_acceptance as acceptance
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import fixture

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from anthroforge.profiling import report

OUTPUT = Path("build/issues-016/profiles").resolve()


def verify_rows(result):
    with ZipFile(result["path"]) as archive:
        events = json.loads(archive.read("trace.json"))["traceEvents"]
    rows = [
        e
        for e in events
        if e.get("cat") == "model" and e.get("args", {}).get("object") == "issueRows"
    ]
    assert not any(e["name"] == "modelReset" for e in rows)
    result["issue_model_events"] = len(rows)


def trials(controller, window):
    point, results = fixture(controller, window, 0.5), []
    for opened in (False, True, True, False):
        prepare_view(controller, window, opened)
        for snapping in (False, True):
            result = acceptance.trial(controller, window, point, snapping, False)
            result["issues_open"] = opened
            verify_rows(result)
            results.append(result)
            (OUTPUT / "acceptance.json").write_text(json.dumps(results, indent=2))
            print(
                json.dumps(dict(issues_open=opened, snapped=snapping, path=result["path"])),
                flush=True,
            )
    return results


def prepare_view(controller, window, opened):
    window.setProperty("issuesOpen", opened)
    QTest.qWait(100)
    height = acceptance.find(window, "viewport").height()
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, height / 330], True)
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
