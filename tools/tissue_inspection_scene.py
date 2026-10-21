"""Hidden GPU evidence for accepted stages, point witnesses and report replay."""

import json
from pathlib import Path

from construction_profile_qualification import shutdown, wait_export
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import scene

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/tissue-inspection")


def frames(controller, renderer, app, name):
    for _ in range(12):
        controller.process_tick()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
        assert not renderer.window.isVisible()
    assert image.save(str(OUTPUT / (name + ".png")))


def comparisons(controller, renderer, app):
    tool = controller.tissue_inspection
    tool.set_view("rest", "base", "Overlay")
    frames(controller, renderer, app, "overlay")
    tool.set_view("rest", "base", "Displacement")
    controller.session.wait()
    frames(controller, renderer, app, "displacement")
    assert tool.summary["state"] == "ready", tool.summary
    tool.arm()
    tool.pick([0, 0, 2], [0, 0, -1])
    controller.session.wait()
    frames(controller, renderer, app, "point")
    assert tool.point and tool.lines
    (OUTPUT / "point.json").write_text(json.dumps(tool.point, indent=2))


def findings(controller, renderer, app, target):
    tool = controller.tissue_inspection
    obstacle(controller)
    controller.session.command("tissue.inspect.check", target=target, stage="rest")
    controller.session.wait()
    records = controller.session.issues.presentation.filtered({}, "", True)
    spatial = [r for r in records if r.get("evidence", {}).get("witness")]
    (OUTPUT / "findings.json").write_text(json.dumps(spatial, indent=2))
    assert spatial
    tool.show_finding(spatial[0]["id"])
    assert tool.finding == spatial[0]["id"] and tool.lines
    frames(controller, renderer, app, "finding")
    return spatial


def obstacle(controller):
    session = controller.session
    key = session.command(
        "import",
        path="examples/primitives/cube.obj",
        units=1,
        parent=session.document.entities[0].id,
    )["entity_id"]
    session.wait()
    session.command("scp.transform", entity=key, values=[0, 0, 0.84, 0, 0, 0, 0.3, 0.3, 0.3])
    session.wait()
    controller.refresh()


def report(controller):
    options = controller.inspection_export.options(str(OUTPUT / "stages.afinspection.zip"))
    controller.session.command("inspection.export", **options, wait=True)


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.timer.stop()
    controller.profiler.collector = collector
    renderer = Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        workload(controller, renderer, app)
        assert not warnings, warnings
    finally:
        shutdown(renderer, controller, collector)


def workload(controller, renderer, app):
    target = scene(controller)
    controller.cameraRequested.emit([0, 0, 0.65, -18, 15, 0, 1.2], True)
    controller.session.command("profile.start")
    comparisons(controller, renderer, app)
    report(controller)
    findings(controller, renderer, app, target)
    controller.session.command("profile.stop", path=str(OUTPUT / "inspection.afprofile.zip"))
    result = wait_export(controller, app)
    assert result["state"] == "saved", result


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run(app)
    print("Hidden tissue stage buffers, point glyphs, geometry findings and frozen report passed.")
