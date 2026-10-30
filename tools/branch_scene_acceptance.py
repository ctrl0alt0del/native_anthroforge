"""Render branched surface seams to textures without creating a visible window."""

from pathlib import Path

import numpy as np
from branch_scene_fixture import create
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from surface_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-branch-scene")


def fixture(controller):
    keys, target = create(controller.session)
    controller.run("surface.branch.add", dict(target=target, boundary=keys[0], curves=keys[2:]))
    controller.session.wait()
    controller.refresh()
    controller.selection_view.select(target)
    controller.cameraRequested.emit([0.5, -0.1, 0.1, -65, 15, 0, 2.1], True)
    return keys, target


def exercise(controller, renderer, app):
    keys, target = fixture(controller)
    assert frames(controller, renderer, app).save(str(OUTPUT / "branch.png"))
    before = controller.render_model.active_rows()[0]
    edit(controller, keys[2])
    assert controller.render_model.active_rows()[0]["handle"] == before["handle"]
    assert frames(controller, renderer, app).save(str(OUTPUT / "edited-branch.png"))
    after = controller.render_model.active_rows()[0]
    assert after["handle"] != before["handle"]
    assert before["handle"] not in controller.render_model.leases
    np.testing.assert_array_equal(controller.pick_handles, [after["handle"]])
    assert controller.session.document.object(target).result.status == "ready"


def edit(controller, key):
    source = controller.session.document.object(key)
    controller.run(
        "curve.point.update",
        dict(curve=source.id, point=source.points[0].id, position=[0.2, 0, 0.3]),
    )
    controller.session.wait()
    controller.refresh()


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        print("Invisible D3D11 branch rendering and displayed-revision replacement passed.")
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
