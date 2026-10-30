"""Hidden D3D11 publication trials; CPU submission timings exclude image readback."""

import json
import os
import sys
from pathlib import Path
from time import perf_counter, sleep

from construction_profile_qualification import shutdown, wait_export
from profile_display_attribution import Attribution
from profile_mesh_adapter import probe
from profiler_system_load import system_load, system_times
from PySide6.QtQuickControls2 import QQuickStyle
from qualify_retained_attachment_edits import load
from shiboken6 import delete
from shortcut_inspection_profile import PLAN, fingerprint

from anthroforge.desktop import offscreen, qt_profiler, runtime
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application


def frame_calls(controller, renderer, app):
    return dict(
        tick=controller.process_tick,
        events=app.processEvents,
        polish=renderer.control.polishItems,
        begin=renderer.control.beginFrame,
        sync=renderer.control.sync,
        render=renderer.control.render,
        end=renderer.control.endFrame,
        presented=controller.frame_presented,
    )


def frame(controller, renderer, app):
    result = {}
    for name, call in frame_calls(controller, renderer, app).items():
        start = perf_counter()
        controller.profiler.call("experiment", name, call)
        result[name] = perf_counter() - start
    result["pending"] = sum(len(m.pending) for m in controller.geometry_models())
    result["active"] = len(controller.session.scheduler.active_jobs)
    return result


def settle(controller, renderer, app, minimum=5):
    rows, start = [], perf_counter()
    while True:
        tick = perf_counter()
        rows.append(frame(controller, renderer, app))
        if len(rows) >= minimum and not rows[-1]["active"] and not rows[-1]["pending"]:
            break
        assert perf_counter() - start < 300, "Viewport trial timed out"
        sleep(max(0, 1 / 60 - (perf_counter() - tick)))
    return rows


def observe(model, records):
    model.rowsInserted.connect(lambda parent, first, last: inserted(model, records, first, last))
    model.rowsRemoved.connect(
        lambda parent, first, last: records.append(dict(removed=last - first + 1))
    )


def inserted(model, records, first, last):
    for row in model.rows[first : last + 1]:
        record = {k: row.get(k) for k in ("id", "handle", "chunk", "revision", "key")}
        mesh = model.leases[row["handle"]]
        record["chunk_bytes"] = max(0, min(16384, mesh.counts[3] - 16384 * row["chunk"])) * 72
        records.append(record)


def capture(controller, renderer, app, output, case):
    session, records = controller.session, []
    observe(controller.render_model, records)
    observe(controller.fiber_display.model, records)
    recording = "--unrecorded" not in sys.argv
    if recording:
        session.command("profile.start", memory_mib=512)
    clock = system_times()
    session.command("driver.value", driver=case["mapping"]["driver"], value=case["value"])
    with Attribution(controller.profiler) as attribution:
        rows = settle(controller, renderer, app)
    result = outcome(controller, renderer, records, clock, rows, attribution)
    result["idle_frames"] = [frame(controller, renderer, app) for _ in range(60)]
    finish(controller, renderer, app, output, result, recording)


def outcome(controller, renderer, records, clock, rows, attribution):
    result = dict(
        load=system_load(clock),
        frames=rows,
        model_events=records,
        errors=controller.session.scheduler.errors,
        visible=renderer.window.isVisible(),
    )
    result["attribution"] = dict(attribution.records)
    return result


def finish(controller, renderer, app, output, result, recording):
    if recording:
        controller.session.command("profile.stop", path=str(output.with_suffix(".afprofile.zip")))
        assert wait_export(controller, app)["state"] == "saved"
    result["fingerprint"] = fingerprint(controller.session)
    result["adapter"] = probe(renderer, controller)
    output.with_suffix(".json").write_text(json.dumps(result), encoding="utf-8")
    assert renderer.frame().save(str(output.with_suffix(".png")))
    print(output.name, result["load"], len(result["frames"]), result["errors"], flush=True)


def exercise(controller, renderer, app, output):
    plan = json.loads(PLAN.read_text())
    load(controller.session, Path(plan["standalone"]))
    controller.refresh()
    controller.selection_view.select("SCP_2")
    controller.viewport_view.frameSelection()
    settle(controller, renderer, app)
    capture(controller, renderer, app, output, plan["cases"][0])


def run(app, output):
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.timer.stop()
    controller.capture_mode = True
    controller.profiler.collector = collector if "--qt" in sys.argv else None
    renderer = offscreen.Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        exercise(controller, renderer, app, output)
        assert not warnings and not renderer.window.isVisible(), warnings
    finally:
        shutdown(renderer, controller, collector)


def main():
    output = Path(sys.argv[1]).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(output.parent / "preferences.json")
    build = Path(os.environ["AF_NATIVE_BUILD"]).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    qt_profiler.build_directory = lambda: build
    QQuickStyle.setStyle("Basic")
    with runtime.native_runtime():
        app = profiler_application()
        try:
            run(app, output)
        finally:
            delete(app)


if __name__ == "__main__":
    main()
