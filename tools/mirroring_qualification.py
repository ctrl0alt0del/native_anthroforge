"""Hidden GPU reflection/picking checks and ordinary runtime profiler workload."""

import json
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from construction_profile_qualification import shutdown, wait_export
from profiler_system_load import system_load, system_times
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from tissue_scene_acceptance import frames, settle

from anthroforge.core.mirroring import MirrorInstance
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from tests.test_tissue_stack_workflow import assembly, current

OUTPUT = Path("build/035-mirroring")


def prepare(controller):
    bone, first, second = assembly(controller.session)
    controller.run("mirror.configure", dict(target=bone, enabled=True, shift=0.8))
    hidden = [
        key for key in controller.session.document.registry.records if key not in (first, second)
    ]
    controller.run("workspace.update", dict(hidden=hidden))
    controller.select(MirrorInstance(second, bone).id)
    settle(controller)
    controller.cameraRequested.emit([0.8, 0, 0.725, -20, 15, 0, 3.5], True)
    return bone, first, second


def capture(controller, renderer, app, name):
    settle(controller)
    image = frames(controller, renderer, app)
    assert image.save(str(OUTPUT / (name + ".png")))
    assert not controller.render_model.pending
    return image


def picking(controller, first, second, bone):
    target = MirrorInstance(second, bone).id
    hover = controller.pick([1.6, 0, 2], [0, 0, -1], 0, False, 0.005)
    clicked = controller.pick([1.6, 0, 2], [0, 0, -1], 0, True, 0.005)
    assert hover["id"] == clicked["id"] == target, (hover, clicked)
    assert controller.selectedData.get("readonly")
    assert target not in controller.scene_projection.records
    source = controller.pick([0, 0, 2], [0, 0, -1], 0, False, 0.005)
    assert source["id"] == second, source


def profile(controller, renderer, app, bone, first, second):
    before = [current(controller.session, key) for key in (first, second)]
    controller.session.command("profile.start")
    load = system_times()
    elapsed = []
    for shift in (0.9, 1.0, 0.85, 0.8):
        started = perf_counter()
        controller.run("mirror.configure", dict(target=bone, shift=shift))
        settle(controller)
        frames(controller, renderer, app)
        elapsed.append((perf_counter() - started) * 1000)
    finish_profile(controller, app, load)
    for key, expected in zip((first, second), before, strict=True):
        np.testing.assert_array_equal(current(controller.session, key), expected)
    return elapsed


def finish_profile(controller, app, load):
    controller.session.command("profile.stop", path=str(OUTPUT / "mirroring.afprofile.zip"))
    (OUTPUT / "background-load.json").write_text(json.dumps(system_load(load), indent=2))
    assert wait_export(controller, app)["state"] == "saved"


def modes(controller, renderer, app):
    for mode in ("SOURCE", "MIRROR", "BOTH"):
        controller.run("workspace.update", dict(mirror_display=mode))
        capture(controller, renderer, app, mode.lower())
    filename = str(OUTPUT / "mirroring.anthroforge")
    controller.session.command("save", path=filename, blocked_policy="wait")


def updates(controller, renderer, app, bone, target):
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.08)))
    capture(controller, renderer, app, "inflation-updated")
    source = controller.session.document.object(target)
    mirror = controller.mirror_records[MirrorInstance(target, bone).id]
    assert mirror["geometry_asset"] == source.result.asset
    assert mirror["geometry_revision"] == source.result.revision
    controller.tissue_inspection.configure("rest", "base", "Displacement")
    settle(controller)
    capture(controller, renderer, app, "mirrored-displacement")
    controller.tissue_inspection.configure("", "", "Overlay")


def qualify(controller, renderer, app, warnings):
    bone, first, second = prepare(controller)
    capture(controller, renderer, app, "both-before")
    picking(controller, first, second, bone)
    elapsed = profile(controller, renderer, app, bone, first, second)
    updates(controller, renderer, app, bone, second)
    modes(controller, renderer, app)
    assert not warnings, warnings
    record(elapsed)


def record(elapsed):
    report = dict(
        plane_edit_wait_refresh_readback_ms=elapsed,
        hover_click_match=True,
        source_geometry_unchanged=True,
        native_reflection_only=True,
        scope="Hidden GPU readback; not physical display/input latency",
    )
    (OUTPUT / "qualification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.profiler.collector = collector
    renderer = Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        qualify(controller, renderer, app, warnings)
    finally:
        shutdown(renderer, controller, collector)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(app)
        finally:
            delete(app)
