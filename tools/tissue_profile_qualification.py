"""Repeatable tissue parameter workload with hidden GPU rendering and runtime reports."""

import json
import sys
from pathlib import Path
from time import perf_counter

from construction_profile_qualification import shutdown, wait_export
from profiler_system_load import system_load, system_times
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from tissue_stacking_scene import frames, prepare, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/022-tissue/profile")


def edits(controller, renderer, app, target):
    elapsed = []
    for value in (0.0002, 0, 0.0004, 0, 0.0006, 0):
        start = perf_counter()
        controller.run(
            "tissue.stacking.configure", dict(target=target, changes=dict(clearance=value))
        )
        settle(controller)
        frames(controller, renderer, app)
        elapsed.append((perf_counter() - start) * 1000)
    return elapsed


def capture(controller, renderer, app, label):
    _, target = prepare(controller)
    frames(controller, renderer, app)
    controller.session.command("profile.start")
    load = system_times()
    elapsed = edits(controller, renderer, app, target)
    context = system_load(load)
    controller.session.command("profile.stop", path=str(OUTPUT / (label + ".afprofile.zip")))
    result = wait_export(controller, app)
    assert result["state"] == "saved", result
    record_measurements(label, elapsed, context)


def record_measurements(label, elapsed, context):
    data = dict(
        edit_wait_render_ms=elapsed,
        background_load=context,
        scope="Commands, jobs, refresh and hidden texture readback; not physical display latency",
    )
    (OUTPUT / (label + ".json")).write_text(json.dumps(data, indent=2))
    print(json.dumps(data), flush=True)


def run(app, label):
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.profiler.collector = collector
    renderer = Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        capture(controller, renderer, app, label)
        assert not warnings, warnings
    finally:
        shutdown(renderer, controller, collector)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(app, sys.argv[1] if len(sys.argv) > 1 else "tissues")
        finally:
            delete(app)
