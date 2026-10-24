"""Bounded production editor profiling without visible windows or physical latency claims."""

import json
import os
import sys
from pathlib import Path
from time import perf_counter

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from anthroforge.desktop import runtime, shortcut_panel  # noqa: E402

if os.environ.get("ANTHROFORGE_PROFILE_RUNTIME"):
    runtime.build_directory = lambda: Path(os.environ["ANTHROFORGE_PROFILE_RUNTIME"])

from construction_profile_qualification import wait_export  # noqa: E402
from probe_ribs_ulna_desktop import prepare  # noqa: E402
from PySide6.QtCore import QObject  # noqa: E402
from PySide6.QtQuickControls2 import QQuickStyle  # noqa: E402
from shiboken6 import delete  # noqa: E402
from shortcut_inspection_profile import PLAN  # noqa: E402

from anthroforge.desktop.app import create_engine  # noqa: E402
from anthroforge.desktop.controller import Controller  # noqa: E402
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application  # noqa: E402


def query_counter():
    original, cost = shortcut_panel.property_state, dict(calls=0, seconds=0.0)

    def measured(*args):
        started = perf_counter()
        try:
            return original(*args)
        finally:
            cost["calls"] += 1
            cost["seconds"] += perf_counter() - started

    shortcut_panel.property_state = measured
    return cost, original


def ticks(controller, application, count):
    intervals = []
    for _ in range(count):
        started = perf_counter()
        controller.tick()
        application.processEvents()
        intervals.append(perf_counter() - started)
    return intervals


def capture(controller, application, plan, output, cost):
    session = controller.session
    session.command("profile.start", seconds=120)
    started = perf_counter()
    key = plan["cases"][0]["mapping"]["driver"]
    controller.shortcut_panel.editValue(key, -1, 3.0, False)
    intervals = ticks(controller, application, 30)
    result = dict(seconds=perf_counter() - started, intervals=intervals, property_queries=cost)
    result.update(active=len(session.scheduler.active_jobs), errors=session.scheduler.errors)
    session.command("profile.stop", path=str(output.with_suffix(".afprofile.zip")))
    assert wait_export(controller, application)["state"] == "saved"
    output.with_suffix(".json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)


def exercise(controller, engine, application, output):
    plan = json.loads(PLAN.read_text())
    prepare(controller, application, Path(plan["standalone"]))
    window = engine.rootObjects()[0]
    header = window.findChild(QObject, "inspectorHeader")
    header.setProperty("shortcuts", True)
    application.processEvents()
    controller.timer.stop()
    cost, original = query_counter()
    try:
        capture(controller, application, plan, output, cost)
    finally:
        shortcut_panel.property_state = original


def run(application, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    collector, controller = QtProfiler(), Controller()
    controller.capture_mode = True
    controller.qt_profiler = collector if "--qt" in sys.argv else None
    warnings = []
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine, application, output)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        collector.close()


def main():
    QQuickStyle.setStyle("Basic")
    with runtime.native_runtime():
        application = profiler_application()
        try:
            run(application, Path(sys.argv[1]).resolve())
        finally:
            delete(application)


if __name__ == "__main__":
    main()
