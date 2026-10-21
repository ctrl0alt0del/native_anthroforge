"""Hidden GPU qualification of stacking witnesses and native field color buffers."""

from pathlib import Path

from construction_profile_qualification import shutdown
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from tissue_scene_acceptance import scene

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/vcp-visual-tools")
VIEW = (0, 0, 4, 1, 0, 0, 0, 1, 0, 0, 0, -1, 300, 1)


def frames(controller, renderer, app, name):
    for _ in range(12):
        controller.process_tick()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
        assert not renderer.window.isVisible()
    assert image.save(str(OUTPUT / (name + ".png")))


def paint(controller, renderer, app):
    target = scene(controller)
    controller.run("tissue.field.create", dict(target=target, name="paint", domain="REST"))
    controller.session.wait()
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0.65, -18, 15, 0, 1.2], True)
    tool = controller.tissue_painting
    tool.begin("paint")
    frames(controller, renderer, app, "paint-before")
    tool.pointer([0, 0], list(VIEW), True)
    tool.timer.stop()
    tool.submit()
    controller.session.wait()
    frames(controller, renderer, app, "paint-preview")
    finish(controller, renderer, app)


def finish(controller, renderer, app):
    tool = controller.tissue_painting
    options = controller.inspection_export.options(str(OUTPUT / "paint.afinspection.zip"))
    controller.session.command("inspection.export", **options, wait=True)
    tool.release()
    controller.session.wait()
    frames(controller, renderer, app, "paint-committed")
    controller.session.wait()
    assert any(controller.session.document.object(tool.target).fields[0].values)
    section(controller, renderer, app)


def section(controller, renderer, app):
    controller.tissue_painting.cancel()
    tool = controller.section_tools
    tool.enable(True)
    tool.timer.stop()
    tool.submit()
    controller.session.wait()
    frames(controller, renderer, app, "section-tissue")
    assert tool.reports and tool.reports[0]["lines"], tool.error
    tool.setting("whole_scene", True)
    tool.timer.stop()
    frames(controller, renderer, app, "section-scene")
    options = controller.inspection_export.options(str(OUTPUT / "section.afinspection.zip"))
    controller.session.command("inspection.export", **options, wait=True)


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.timer.stop()
    renderer = Offscreen(controller, warnings)
    try:
        paint(controller, renderer, app)
        assert not warnings, warnings
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
    print("Hidden painting colors, commit and frozen inspection report passed.")
