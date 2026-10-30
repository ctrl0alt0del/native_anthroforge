"""Texture-only drawing acceptance and runtime report; never shows a desktop window."""

import json
from pathlib import Path

from PIL import Image, ImageDraw
from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-drawing-scene")


def frames(controller, renderer, app, count=6):
    for _ in range(count):
        assert not renderer.window.isVisible()
        for model in (controller.render_model, controller.image_model, controller.path_model):
            model.drain()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def reference(controller):
    image = Image.new("RGB", (512, 256), "#e0d5bc")
    draw = ImageDraw.Draw(image)
    draw.line([(64, 170), (190, 70), (310, 75), (450, 155)], fill="#756a55", width=6)
    source = OUTPUT / "guide.png"
    image.save(source)
    result = controller.run("image.import", dict(path=str(source), width=2))
    controller.session.wait(5)
    controller.refresh()
    controller.selection_view.select(result["object_id"])
    controller.run("image.presentation", dict(target=result["object_id"], depth="BACK"))
    controller.cameraRequested.emit([0, 0, 0, -90, 0, 0, 3], True)
    return result["object_id"]


def pointer(x, y):
    return [x, y, 3, 0, 0, -1, 500 + x * 200, 500 + y * 200, 1]


def exercise(controller, renderer, app):
    target = reference(controller)
    renderer.root.setProperty("gridVisible", False)
    frames(controller, renderer, app)
    controller.session.command("profile.start")
    tool = controller.drawing_tools
    tool.setting("depth", "IMAGE")
    tool.begin("DRAW")
    tool.pointer(pointer(-0.75, -0.2), [0, 0, -1], True)
    for x, y in ((-0.25, 0.2), (0.25, 0.2), (0.75, -0.1)):
        tool.pointer(pointer(x, y), [0, 0, -1], False)
    frames(controller, renderer, app).save(str(OUTPUT / "provisional.png"))
    tool.release()
    qualify_curve(controller, renderer, app, target)


def qualify_curve(controller, renderer, app, target):
    controller.session.wait(5)
    controller.refresh()
    image = frames(controller, renderer, app)
    image.save(str(OUTPUT / "accepted.png"))
    curves = [o for o in controller.session.document.objects if o.id != target]
    assert len(curves) == 1 and not curves[0].parent and not curves[0].owners
    assert all(abs(p.position[2]) < 1e-8 for p in curves[0].points)
    assert controller.path_model.active_rows()
    display_check(controller, renderer, image, curves[0])
    controller.run("object.delete", dict(target=target))
    assert controller.session.document.object(curves[0].id) == curves[0]
    finish_report(controller)


def display_check(controller, renderer, image, curve):
    for index in (0, len(curve.points) // 2, -1):
        point = curve.points[index].position
        pixel = project(renderer, point)
        colors = [
            image.pixelColor(round(pixel.x()) + x, round(pixel.y()) + y)
            for x in range(-3, 4)
            for y in range(-3, 4)
        ]
        assert any(c.blue() > 190 and c.red() > 150 and c.green() < 190 for c in colors), point
        hit = controller.selection_view.pick([point[0], point[1], 3], [0, 0, -1], 0, False, 0.01)
        assert hit["id"] == curve.id


def project(renderer, point):
    return QMetaObject.invokeMethod(
        renderer.root,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(v)) for v in point),
    )


def finish_report(controller):
    status = controller.session.command(
        "profile.stop", path=str(OUTPUT / "drawing.afprofile.zip"), wait=True
    )
    assert status["state"] == "saved", status
    assert not controller.message, controller.message


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        conversion_scene(controller, renderer, app)
        repeated_strokes(controller)
        assert not warnings, warnings
        print(json.dumps(dict(passed=True, visible_window=False, image_dependency=False)))
    finally:
        renderer.close()
        controller.close()


def conversion_scene(controller, renderer, app):
    points = [dict(position=p) for p in ((-0.6, -0.45, 0.2), (0, -0.1, 0.2), (0.6, -0.45, 0.2))]
    key = controller.run("curve.create", dict(points=points))
    controller.session.wait(5)
    controller.refresh()
    before = controller.session.document.object(key)
    result = controller.run(
        "curve.conversion.preview", dict(curve=key, engine="POLYLINE", mode="AUTHORED")
    )
    controller.session.wait(5)
    controller.refresh()
    image = frames(controller, renderer, app)
    image.save(str(OUTPUT / "conversion-preview.png"))
    assert_preview_pixel(renderer, image, [-0.3, -0.275, 0.2])
    assert_conversion_accept(controller, key, result["token"], before)


def assert_preview_pixel(renderer, image, point):
    pixel = project(renderer, point)
    colors = [
        image.pixelColor(round(pixel.x()) + x, round(pixel.y()) + y)
        for x in range(-3, 4)
        for y in range(-3, 4)
    ]
    assert any(c.green() > c.red() + 30 and c.green() > c.blue() + 20 for c in colors)


def assert_conversion_accept(controller, key, token, before):
    assert all(
        not row["pickable"] for row in controller.path_model.active_rows() if row.get("preview")
    )
    controller.run("curve.conversion.accept", dict(token=token))
    controller.session.wait(5)
    controller.refresh()
    assert controller.session.document.object(key).engine == "POLYLINE"
    controller.run("undo", {})
    assert controller.session.document.object(key).points == before.points


def repeated_strokes(controller):
    tool = controller.drawing_tools
    tool.cancel()
    tool.setting("depth", "VIEW")
    tool.setting("method", "POLYLINE")
    tool.begin("DRAW")
    for closed in (True, False):
        stroke_undo(controller, tool, closed)
    before = controller.session.document
    tool.pointer(pointer(0, 0), [0, 0, 1], True)
    tool.cancel()
    assert controller.session.document is before


def stroke_undo(controller, tool, closed):
    before = controller.session.history.cursor
    points = [(0, 0), (0.4, 0), (0.4, 0.4), (0.02 if closed else 0.8, 0)]
    for index, (x, y) in enumerate(points):
        tool.pointer(pointer(x, y), [0, 0, 1], index == 0)
    tool.release()
    controller.session.wait(5)
    curve = controller.session.document.objects[-1]
    assert curve.closed == closed and tool.mode == "DRAW" and tool.stroke is None
    assert controller.session.history.cursor == before + 1
    controller.run("undo", {})
    assert curve.id not in controller.session.document.registry.records


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
