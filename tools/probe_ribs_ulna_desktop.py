"""Background-only production QML profiling; no physical display latency claim."""

import os
import sys
from pathlib import Path
from time import perf_counter, sleep

from construction_profile_qualification import wait_export
from probe_ribs_ulna_latency import geometry, job_record, lineage, observe, write
from PySide6.QtQuickControls2 import QQuickStyle
from qualify_retained_attachment_edits import load
from ribs_ulna_equivalence import attachments
from ribs_ulna_queue_probe import monitor, prioritize
from shiboken6 import delete

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime


def settle(controller, app):
    deadline = perf_counter() + 240
    while controller.session.scheduler.active_jobs or any(
        m.pending for m in controller.geometry_models()
    ):
        assert perf_counter() < deadline, "Desktop did not settle."
        app.processEvents()
        sleep(0.002)
    for _ in range(5):
        app.processEvents()
        sleep(0.02)


def displayed(controller, output):
    previous = [{}]

    def updated():
        poses = {r["id"]: r.get("matrix") for r in controller.render_model.active_rows()}
        changes = [key for key, value in poses.items() if previous[0].get(key) != value]
        if changes:
            output.append(dict(time=perf_counter(), ids=changes))
            previous[0] = poses

    controller.render_model.activated.connect(updated)


def prepare(controller, app, source):
    load(controller.session, source)
    controller.refresh()
    controller.select("SCP_2")
    controller.shortcut_panel.configure(True, False, "")
    settle(controller, app)


def finish(controller, app, output, rows, poses, views, started):
    elapsed = perf_counter() - started
    if "--unrecorded" not in sys.argv:
        controller.session.command("profile.stop", path=str(output / "edit.afprofile.zip"))
        assert wait_export(controller, app)["state"] == "saved"
    write(output / "timing.json", dict(started=started, seconds=elapsed))
    write(output / "queue.json", rows)
    write(output / "poses.json", poses)
    write(output / "views.json", views)
    write(output / "geometry.json", geometry(controller.session))
    write(output / "attachments.json", attachments(controller.session))
    write(output / "jobs.json", [job_record(j) for j in controller.session.scheduler.jobs])
    print(dict(seconds=elapsed, errors=controller.session.scheduler.errors), flush=True)


def capture(controller, app, output):
    session = controller.session
    driver = next(d for d in session.document.driving_shortcuts if d.label == "Ribs Top Radius")
    write(output / "ulna-prerequisites.json", lineage(session))
    poses, views, started = [], [], perf_counter()
    observe(session, poses, started)
    displayed(controller, views)
    rows = monitor(session.scheduler)
    if "--priority-probe" in sys.argv:
        prioritize(session.scheduler)
    if "--unrecorded" not in sys.argv:
        session.command("profile.start", seconds=240, memory_mib=512)
    controller.shortcut_panel.editValue(driver.id, -1, 3.0, False)
    settle(controller, app)
    finish(controller, app, output, rows, poses, views, started)


def collector_for_run():
    return None if "--application-only" in sys.argv or "--unrecorded" in sys.argv else QtProfiler()


def run(app, source, output):
    output.mkdir(parents=True, exist_ok=True)
    collector = collector_for_run()
    controller, warnings = Controller(), []
    controller.capture_mode, controller.qt_profiler = True, collector
    engine = create_engine(controller, warnings)
    try:
        prepare(controller, app, source)
        capture(controller, app, output)
        write(output / "qml-warnings.json", warnings)
    finally:
        controller.close()
        delete(engine)
        if collector:
            collector.close()


if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(app, *(Path(value).resolve() for value in sys.argv[1:3]))
        finally:
            delete(app)
