"""Inspect branched, opposite-side envelopes on a hidden GPU texture."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_shapes_acceptance import capture

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime
from tests.test_tissue_parts_workflow import branched_tissue


def exercise(controller, renderer, app):
    _, target, branch = branched_tissue(controller.session)
    controller.refresh()
    controller.select(target)
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.15)))
    controller.run("tissue.connector", dict(target=target, part=branch, width=0.3, fullness=0.03))
    controller.run("tissue.configure", dict(target=target, changes=dict(both_sides=True)))
    capture(controller, renderer, app, "branch-envelope")
    controller.run("tissue.inflation", dict(target=target, side="b", changes=dict(enabled=False)))
    capture(controller, renderer, app, "branch-zero-side")


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
        print("Hidden GPU branch envelope and zero-side composition passed.")
