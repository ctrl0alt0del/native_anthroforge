"""Texture-only Fiber radius rendering and exact picking; no visible native window."""

from pathlib import Path

from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/parity-workflows-034/fiber-display")


def frames(controller, renderer, app):
    for _ in range(12):
        assert not renderer.window.isVisible()
        for model in controller.geometry_models():
            model.drain()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def setup(controller):
    target = controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1.0)
    )["entity_id"]
    controller.session.wait(5)
    controller.run(
        "fiber.place",
        dict(points=[dict(position=[x, 0, 0.501], target=target) for x in (-0.4, 0.4)]),
    )
    controller.session.wait(5)
    key = controller.session.document.objects[0].id
    controller.run("workspace.update", dict(hidden=[target]))
    controller.select(key)
    controller.authoring.setEditing(False)
    return key


def capture(controller, renderer, app, key, radius):
    controller.run("fiber.presentation", dict(target=key, radius=radius))
    controller.session.wait(5)
    image = frames(controller, renderer, app)
    image.save(str(OUTPUT / f"radius-{radius}.png"))
    middle = controller.session.resources.paths[
        controller.session.document.object(key).result.asset
    ].path.array()
    point = middle[len(middle) // 2, :3]
    pixel = project(renderer, point)
    colors = [image.pixelColor(round(pixel.x()), round(pixel.y()) + y) for y in range(-40, 41)]
    return sum(c.red() > 200 and 100 < c.green() < 210 and c.blue() < 180 for c in colors)


def project(renderer, point):
    return QMetaObject.invokeMethod(
        renderer.root,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(v)) for v in point),
    )


def exercise(controller, renderer, app):
    key = setup(controller)
    renderer.root.setProperty("gridVisible", False)
    controller.cameraRequested.emit([0, 0, 0.501, -90, 0, 0, 2], True)
    small = capture(controller, renderer, app, key, 0.005)
    large = capture(controller, renderer, app, key, 0.04)
    assert large > small >= 1, (small, large)
    assert controller.fiber_display.hits([0, 0.03, 3], [0, 0, -1])
    assert not controller.message, controller.message
    print(f"Texture-only Fiber radius: narrow={small}px, wide={large}px; exact picking passed.")


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
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
