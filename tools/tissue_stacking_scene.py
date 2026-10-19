"""Texture-only inspection of muscle and mixed-shell stacking; never opens a window."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime
from tests.test_tissue_mixed_stacking import normal
from tests.test_tissue_stack_workflow import assembly, current


def prepare(controller):
    _, first, second = assembly(controller.session)
    for key, color in ((first, "#5b91bc"), (second, "#c98668")):
        controller.run("tissue.configure", dict(target=key, changes=dict(color=color)))
    hidden = [
        key for key in controller.session.document.registry.records if key not in (first, second)
    ]
    controller.run("workspace.update", dict(hidden=hidden))
    controller.select(second)
    settle(controller)
    controller.cameraRequested.emit([0, 0, 0.725, -12, 20, 0, 1.15], True)
    return first, second


def capture(controller, renderer, app, name, target):
    settle(controller)
    current(controller.session, target)
    assert frames(controller, renderer, app).save(
        str(Path("build/022-tissue") / (name + "-gpu.png"))
    )
    hover = controller.pick([0, 0, 2], [0, 0, -1], 0, False, 0.005)
    clicked = controller.pick([0, 0, 2], [0, 0, -1], 0, True, 0.005)
    assert hover["id"] == clicked["id"] == target


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        first, second = prepare(controller)
        capture(controller, renderer, app, "stacked-muscles", second)
        normal(controller.session, second, relaxed=True)
        capture(controller, renderer, app, "stacked-relaxed-shell", second)
        normal(controller.session, first)
        capture(controller, renderer, app, "stacked-shells", second)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden GPU mixed stacking, geometry replacement and matching picking passed.")
