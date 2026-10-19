"""Inspect relaxed tissue on a hidden GPU texture, with retained exact backing."""

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import scene, settle
from tissue_shapes_acceptance import capture

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def exercise(controller, renderer, app):
    target = scene(controller)
    controller.run("tissue.inflation", dict(target=target, changes=dict(mode="NORMAL", amount=0.2)))
    settle(controller)
    controller.run("tissue.constraint.add", dict(target=target, mask="BOUNDARY"))
    changes = dict(mode="STATIC_PBD", iterations=40, sagginess=0.5, gravity=[1, 0, -1])
    controller.run("tissue.relaxation", dict(target=target, changes=changes))
    capture(controller, renderer, app, "static-envelope")
    item = controller.session.document.object(target)
    assert item.diagnostics[0].max_fixed_error == 0
    assert item.diagnostics[0].status in ("CONVERGED", "ITERATION_LIMIT")


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden GPU constrained static envelope passed.")
