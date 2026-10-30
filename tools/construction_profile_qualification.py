"""Serial routed-fiber gestures and shared consumers, with invisible texture readback."""

import gc
import json
from pathlib import Path
from time import perf_counter, sleep
from zipfile import ZipFile

from profiler_system_load import system_load, system_times
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from surface_scene_acceptance import frames

from anthroforge.core.fibers import Fiber
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.controller_actions import new_document
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-construction-profile")
PROJECT = Path("build/020-skull-scene/skull.anthroforge").resolve()


def prepare(controller, renderer, app):
    session = controller.session
    session.command("open", path=str(PROJECT))
    sources = [o.id for o in session.document.objects if isinstance(o, Fiber)]
    for index in range(3):
        session.command("surface.create", curves=sources[:2], name=f"Shared loft {index}", strips=7)
    session.wait(15)
    controller.refresh()
    controller.selection_view.select(sources[0])
    controller.authoring.setEditing(True)
    row = next(r for r in controller.authoring.componentRows if r["part"] == "position")
    controller.authoring.selectComponent(row["key"], False)
    frames(controller, renderer, app, 15)


def gesture(controller, renderer, app):
    intervals = []
    assert controller.viewport_view.beginTransform("Move")
    for index in range(32):
        started = perf_counter()
        controller.viewport_view.transformDelta([index * 0.0002, 0, 0, 0, 0, 0, 1, 1, 1])
        controller.session.scheduler.tick()
        controller.refresh()
        frames(controller, renderer, app, 1)
        controller.profiler.status()
        intervals.append((perf_counter() - started) * 1000)
    controller.viewport_view.endTransform(False)
    controller.session.wait(15)
    controller.refresh()
    return intervals


def capture_report(controller, index, app):
    path = OUTPUT / f"shared-fibers-{index}.afprofile.zip"
    controller.session.command("profile.stop", path=str(path))
    status = wait_export(controller, app)
    assert status["state"] == "saved", status
    with ZipFile(path) as archive:
        summary = json.loads(archive.read("summary.json"))
        manifest = json.loads(archive.read("manifest.json"))
    assert manifest["complete"], manifest["losses"]
    return dict(path=str(path), summary=summary, complete=manifest["complete"])


def wait_export(controller, app):
    deadline = perf_counter() + 15
    status = controller.profiler.status()
    while status["state"] not in ("saved", "export_failed"):
        assert perf_counter() < deadline, status
        app.processEvents()
        sleep(0.005)
        status = controller.profiler.status()
    return status


def trial(controller, renderer, app, index, recording):
    prepare(controller, renderer, app)
    if recording:
        controller.session.command("profile.start")
    load = system_times()
    intervals = gesture(controller, renderer, app)
    context = system_load(load)
    frames(controller, renderer, app, 5)
    assert all(o.result.status == "ready" for o in controller.session.document.objects)
    report = capture_report(controller, index, app) if recording else {}
    return dict(index=index, recording=recording, frame_work_ms=intervals, load=context, **report)


def trials(controller, renderer, app):
    values = []
    for index, recording in enumerate((False, True, True, False)):
        result = trial(controller, renderer, app, index, recording)
        values.append(result)
        report = dict(
            trials=values,
            scope="Gesture/refresh/render plus synchronous texture readback; no display latency",
        )
        (OUTPUT / "measurements.json").write_text(json.dumps(report, indent=2))
        print(index, recording, result["load"], flush=True)
    release_scene(controller, renderer, app)


def release_scene(controller, renderer, app):
    controller.session.command("profile.start")
    new_document(controller)
    controller.session.wait(15)
    controller.refresh()
    frames(controller, renderer, app, 15)
    gc.collect()
    report = capture_report(controller, "release", app)
    memory = report["summary"]["diagnostics"]["geometry_memory"]["latest"]
    assert memory["unique_bytes"] == 0, memory
    print("Document, history, job and viewport geometry released after New.", flush=True)


def run(app):
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.profiler.collector = collector
    renderer = Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        trials(controller, renderer, app)
        assert not warnings, warnings
    finally:
        shutdown(renderer, controller, collector)


def shutdown(renderer, controller, collector):
    renderer.close()
    controller.close()
    collector.close()
    delete(renderer.root)
    delete(renderer.engine)
    delete(renderer.window)
    delete(renderer.control)
    print("Construction profiling and offscreen resource shutdown passed.", flush=True)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(app)
        finally:
            delete(app)
