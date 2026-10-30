"""Reference images rendered to a GPU texture, with no visible window or desktop input."""

import json
from pathlib import Path

from PIL import Image, ImageDraw
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-image-scene")


def frames(controller, renderer, app, count=6):
    for _ in range(count):
        assert not renderer.window.isVisible()
        controller.image_model.drain()
        controller.render_model.drain()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def source():
    image = Image.new("RGB", (512, 300))
    draw = ImageDraw.Draw(image)
    for rectangle, color in (
        ((0, 0, 255, 149), "red"),
        ((256, 0, 511, 149), "lime"),
        ((0, 150, 255, 299), "blue"),
        ((256, 150, 511, 299), "yellow"),
    ):
        draw.rectangle(rectangle, fill=color)
    image.save(OUTPUT / "quadrants.png")
    return str(OUTPUT / "quadrants.png")


def fixture(controller):
    result = controller.run("image.import", dict(path=source(), width=2))
    controller.session.wait(5)
    controller.refresh()
    target = result["object_id"]
    controller.run("image.presentation", dict(target=target, opacity=1))
    controller.selection_view.select(target)
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, 3], True)
    return target


def color_at(renderer, image, point):
    pixel = QMetaObject.invokeMethod(
        renderer.root,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(v)) for v in point),
    )
    color = image.pixelColor(round(pixel.x()), round(pixel.y()))
    return [color.red(), color.green(), color.blue()]


def orientation(renderer, image):
    expected = (
        (-0.5, 0.3, [255, 0, 0]),
        (0.5, 0.3, [0, 255, 0]),
        (-0.5, -0.3, [0, 0, 255]),
        (0.5, -0.3, [255, 255, 0]),
    )
    for x, y, color in expected:
        actual = color_at(renderer, image, [x, y, 0])
        assert all(abs(a - b) < 15 for a, b in zip(actual, color, strict=True)), (actual, color)


def exercise(controller, renderer, app):
    renderer.root.setProperty("gridVisible", False)
    target = fixture(controller)
    axis_visibility(controller, renderer, app, target)
    image = frames(controller, renderer, app)
    image.save(str(OUTPUT / "quadrants-view.png"))
    orientation(renderer, image)
    hit = controller.selection_view.pick([-0.5, 0.3, 2], [0, 0, -1], 0, False, 0.02)
    assert hit["id"] == target and abs(hit["uv"][0] - 0.25) < 1e-8
    assert controller.selection_view.pick([-0.5, 0.3, 2], [0, 0, -1], 0, True, 0.02) == hit
    for depth in ("FRONT", "BACK", "NORMAL"):
        controller.run("image.presentation", dict(target=target, depth=depth))
        orientation(renderer, frames(controller, renderer, app))
    editing(controller, renderer, app, target)


def editing(controller, renderer, app, target):
    calibration(controller, target)
    frames(controller, renderer, app)
    depth_occlusion(controller, renderer, app, target)
    replacement(controller, renderer, app, target)


def axis_visibility(controller, renderer, app, target):
    controller.run("image.presentation", dict(target=target, only_axis_aligned=True))
    for depth in ("NORMAL", "FRONT", "BACK"):
        controller.run("image.presentation", dict(target=target, depth=depth))
        for orthographic in (True, False):
            for angle, visible in ((-90, True), (-70, False)):
                controller.cameraRequested.emit([0, 0, 0, angle, 0, 0, 3], orthographic)
                image = frames(controller, renderer, app)
                check_axis_view(controller, renderer, image, target, visible)
    image.save(str(OUTPUT / "axis-hidden.png"))
    controller.run(
        "image.presentation", dict(target=target, only_axis_aligned=False, depth="NORMAL")
    )
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, 3], True)


def check_axis_view(controller, renderer, image, target, visible):
    color = color_at(renderer, image, [-0.5, 0.3, 0])
    assert (color[0] > 200 and color[1] < 30) == visible, (color, visible)
    hit = controller.selection_view.pick([-0.5, 0.3, 2], [0, 0, -1], 0, False, 0.02)
    assert (hit.get("id") == target) == visible, (hit, visible)


def calibration(controller, target):
    original = controller.session.document.object(target)
    cursor = controller.session.history.cursor
    controller.image_tools.start()
    controller.image_tools.probe([-0.5, 0, 2], [0, 0, -1], True)
    controller.image_tools.probe([0.5, 0, 2], [0, 0, -1], True)
    assert len(controller.image_tools.points) == 2
    controller.image_tools.accept(2)
    assert controller.session.document.object(target).width == 4
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert controller.session.document.object(target) == original


def depth_occlusion(controller, renderer, app, target):
    result = controller.run("import", dict(path="examples/primitives/cube.obj", units=0.5))
    controller.session.wait(5)
    controller.refresh()
    for depth in ("FRONT", "BACK", "NORMAL"):
        controller.run("image.presentation", dict(target=target, depth=depth))
        image = frames(controller, renderer, app)
        color = color_at(renderer, image, [0.18, 0.18, 0])
        image.save(str(OUTPUT / ("occlusion-" + depth + ".png")))
        assert (color[1] > 240 and color[0] < 15 and color[2] < 15) == (depth == "FRONT"), (
            depth,
            color,
        )
    controller.run("workspace.update", dict(hidden=[result["entity_id"]]))
    frames(controller, renderer, app)


def replacement(controller, renderer, app, target):
    old = controller.image_model.active_rows()[0]
    path = OUTPUT / "replacement.png"
    Image.new("RGB", (1024, 1024), "purple").save(path)
    controller.run("image.replace", dict(target=target, path=str(path)))
    controller.session.wait(5)
    controller.refresh()
    assert controller.image_model.active_rows()[0] == old
    frames(controller, renderer, app, 1)
    assert controller.image_model.active_rows()[0]["handle"] == old["handle"]
    frames(controller, renderer, app, 12).save(str(OUTPUT / "replacement-view.png"))
    assert controller.image_model.active_rows()[0]["handle"] != old["handle"]
    assert old["handle"] not in controller.image_model.leases


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        print(json.dumps(dict(passed=True, visible_window=False, orientation=True, staged=True)))
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
