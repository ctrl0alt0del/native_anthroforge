"""Inspect routed skull fibers and their loft through an invisible D3D11 render target."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from skull_construction_fixture import create
from surface_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-skull-scene")


def exercise(controller, renderer, app):
    targets, curves = create(controller.session, OUTPUT)
    controller.refresh()
    controller.selection_view.select(curves[0])
    controller.cameraRequested.emit([0.15, -0.45, 1.35, -10, 30, 0, 3], True)
    assert frames(controller, renderer, app, 20).save(str(OUTPUT / "skull-fibers.png"))
    controller.cameraRequested.emit([0.15, -0.45, 1.35, 0, 0, 0, 3], True)
    assert frames(controller, renderer, app).save(str(OUTPUT / "skull-front.png"))
    save_construction_views(controller, renderer, app, targets)
    assert len(controller.path_model.active_rows()) == 4
    assert all(o.result.status == "ready" for o in controller.session.document.objects)


def save_construction_views(controller, renderer, app, targets):
    controller.run("workspace.update", dict(hidden=targets))
    assert frames(controller, renderer, app).save(str(OUTPUT / "paths-and-loft.png"))
    controller.run("workspace.update", dict(hidden=[]))
    controller.session.command(
        "save", path=str(OUTPUT / "skull.anthroforge"), blocked_policy="wait"
    )


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        print("Invisible skull Fiber creation, routed conversion, loft and save passed.")
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
