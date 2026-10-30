"""Texture-only native Parametric/consumer rendering; never creates a visible window."""

import json
from pathlib import Path

import numpy as np
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/shortcuts-scene-review")


def scene(controller):
    curve = controller.run("curve.create", dict(engine="PARAMETRIC", settings=settings()))
    controller.session.wait(5)
    body = controller.run("primitive.from_curves", dict(curves=[curve], kind="BODY"))
    controller.session.wait(5)
    controller.refresh()
    controller.selection_view.select(body)
    controller.cameraRequested.emit([0, 0, 0.1, 70, 0, 0, 1.2], True)
    return curve, body


def settings():
    return dict(
        x="r*cos(t)",
        y="r*sin(t)",
        z="t*0.04*m",
        resolution=48,
        interval=dict(end=4.5),
        variables=[dict(name="r", value=0.25, dimension="LENGTH")],
    )


def frames(controller, renderer, application):
    controller.session.wait(10)
    controller.refresh()
    for _ in range(6):
        assert not renderer.window.isVisible()
        controller.path_model.drain()
        controller.render_model.drain()
        QTest.qWait(30)
        image = renderer.frame()
        controller.frame_presented()
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    return image


def geometry(controller, body):
    item = controller.session.document.entity(body)
    return controller.session.assets[item.result.asset].mesh.array(0).copy()


def exercise(controller, renderer, application):
    curve, body = scene(controller)
    image = frames(controller, renderer, application)
    assert image.save(str(OUTPUT / "parametric-body.png"))
    before = geometry(controller, body)
    change_radius(controller, curve)
    image = frames(controller, renderer, application)
    assert image.save(str(OUTPUT / "radius-edited.png"))
    assert not np.allclose(geometry(controller, body), before)
    controller.run("undo", {})
    frames(controller, renderer, application)
    np.testing.assert_array_equal(geometry(controller, body), before)
    generated_controls(controller, renderer, application, curve)


def change_radius(controller, curve):
    variable = controller.session.document.object(curve).engine_settings.variables[0].id
    controller.run(
        "curve.parametric.variable.update",
        dict(curve=curve, variable=variable, changes=dict(value=0.4)),
    )


def generated_controls(controller, renderer, application, curve):
    controller.selection_view.select(curve)
    controller.authoring.setEditing(True)
    image = frames(controller, renderer, application)
    assert image.save(str(OUTPUT / "generated-controls.png"))
    assert controller.path_model.active_rows()[0]["geometry_revision"] > 0


def run(application):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, application)
        assert not warnings, warnings
        (OUTPUT / "acceptance.json").write_text(
            json.dumps(
                dict(passed=True, renderer="D3D11 texture", visible_window=False, interactive=False)
            )
        )
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    with native_runtime():
        run(application)
    print("Native texture-only Parametric rendering, consumer update and undo passed.")
