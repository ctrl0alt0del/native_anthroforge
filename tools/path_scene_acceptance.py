"""GPU texture-only path publication and picking checks; no visible window or input."""

import json
from pathlib import Path

from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.application.curve_sources import world
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-path-scene")


def frames(controller, renderer, app, count=4):
    for _ in range(count):
        assert not renderer.window.isVisible()
        controller.path_model.drain()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def fixture(controller):
    points = [dict(position=p) for p in ((-0.6, 0, 0), (-0.2, 0, 0.6), (0.4, 0, 0.4), (0.7, 0, 0))]
    key = controller.run("curve.create", dict(points=points, name="Standalone path"))
    controller.session.wait(5)
    controller.refresh()
    controller.selection_view.select(key)
    controller.cameraRequested.emit([0, 0, 0.25, 0, 0, 0, 2.5], True)
    return key


def check_replacement(controller, renderer, app, key):
    before = controller.path_model.active_rows()[0]
    curve = controller.session.document.object(key)
    controller.run(
        "curve.point.update", dict(curve=key, point=curve.points[1].id, position=[-0.2, 0, 0.9])
    )
    controller.session.wait(5)
    controller.refresh()
    assert controller.path_model.active_rows()[0]["handle"] == before["handle"]
    assert controller.path_model.leases[before["handle"]]
    frames(controller, renderer, app)
    current = controller.path_model.active_rows()[0]
    assert current["handle"] != before["handle"]
    assert controller.path_handles.tolist() == [current["handle"]]
    assert before["handle"] not in controller.path_model.leases


def exercise(controller, renderer, app):
    key = fixture(controller)
    image = frames(controller, renderer, app)
    assert image.save(str(OUTPUT / "standalone-curve.png"))
    row = controller.path_model.active_rows()[0]
    assert row["id"] == key and row["geometry_revision"] > 0
    hit = controller.selection_view.pick([-0.6, -2, 0], [0, 1, 0], 0, False, 0.02)
    assert hit["id"] == key
    assert controller.selection_view.pick([-0.6, -2, 0], [0, 1, 0], 0, True, 0.02) == hit
    check_replacement(controller, renderer, app, key)
    frames(controller, renderer, app).save(str(OUTPUT / "edited-curve.png"))
    affine_parenting(controller, renderer, app, key)


def affine_parenting(controller, renderer, app, key):
    parent = controller.run("curve.create", dict(name="Transform parent"))
    controller.run("object.reparent", dict(target=key, parent=parent))
    controller.run("object.transform", dict(target=parent, values=[0, 0, 0, 0, 0, 0, 1.3, 1, 0.6]))
    controller.run("object.transform", dict(target=key, values=[0, 0, 0, 0, 35, 0, 1, 1, 1]))
    controller.run("workspace.update", dict(hidden=[parent]))
    controller.session.wait(5)
    controller.refresh()
    image = frames(controller, renderer, app)
    frame = world(controller.session.engine, controller.session.document, key)
    point = controller.session.document.object(key).points[1].position
    pixel_check(renderer, image, controller.session.engine.world_point(frame, point))
    image.save(str(OUTPUT / "affine-parenting.png"))


def pixel_check(renderer, image, position):
    pixel = QMetaObject.invokeMethod(
        renderer.root,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(v)) for v in position),
    )
    colors = [
        image.pixelColor(round(pixel.x()) + x, round(pixel.y()) + y)
        for x in range(-4, 5)
        for y in range(-4, 5)
    ]
    assert any(c.red() > 120 and c.red() > c.blue() * 1.4 for c in colors), position


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        report()
    finally:
        renderer.close()
        controller.close()


def report():
    result = dict(
        passed=True,
        renderer="QQuickRenderControl/D3D11",
        visible_window=False,
        picking="displayed revision",
        replacement="old complete path retained",
    )
    (OUTPUT / "acceptance.json").write_text(json.dumps(result))
    print(json.dumps(result))


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
