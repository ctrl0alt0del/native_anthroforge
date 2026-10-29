"""Inspect actual brush colors and unchanged controls using hidden GPU rendering."""

import json
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime
from tests.test_skin_painting_view import brush as collagen_brush
from tests.test_tissue_painting_view import brush as tissue_brush

OUTPUT = Path("build/painting/visual")
VIEW = [0.5, 0.2, 4, 1, 0, 0, 0, 1, 0, 0, 0, -1, 300, 1]


def capture(controller, renderer, app, name, angle):
    settle(controller)
    assert frames(controller, renderer, app).save(str(OUTPUT / f"{name}-{angle}.png"))
    assert not renderer.window.isVisible()


def inspect(controller, renderer, app, name, factory):
    target, tool = factory(controller)
    tool.setting("radius", 70)
    tool.setting("through", False)
    before = controller.session.document
    for angle in (0, 45):
        painted_view(controller, renderer, app, tool, name, angle)
    assert tool.preview and controller.session.document.objects == before.objects
    tool.cancelStroke()
    capture(controller, renderer, app, name + "-cancelled", 0)
    assert not tool.preview and controller.session.document.objects == before.objects
    return dict(consumer=name, target=target, window_visible=False, authored_changed=False)


def painted_view(controller, renderer, app, tool, name, angle):
    tool.cancelStroke()
    controller.cameraRequested.emit([0.5, 0.2, 0.5, -55, angle, 0, 2], True)
    frames(controller, renderer, app)
    tool.pointer([0, 0], VIEW, True)
    controller.session.wait()
    capture(controller, renderer, app, name, angle)


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    evidence = []
    for name, factory in (("tissue", tissue_brush), ("collagen", collagen_brush)):
        controller, warnings = Controller(), []
        renderer = Offscreen(controller, warnings)
        try:
            evidence.append(inspect(controller, renderer, app, name, factory))
            assert not warnings, warnings
        finally:
            renderer.close()
            controller.close()
    (OUTPUT / "evidence.json").write_text(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        run(QGuiApplication([]))
