"""GPU texture-only construction point rendering; no visible window or desktop input."""

from pathlib import Path

from PySide6.QtCore import Q_ARG, Q_RETURN_ARG, QMetaObject, QPointF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def frames(controller, renderer, app):
    for _ in range(6):
        assert not renderer.window.isVisible()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def marker(renderer, image, position):
    pixel = QMetaObject.invokeMethod(
        renderer.root,
        "projectPoint",
        Q_RETURN_ARG(QPointF),
        *(Q_ARG(float, float(v)) for v in position),
    )
    colors = [
        image.pixelColor(round(pixel.x()) + x, round(pixel.y()) + y)
        for x in range(-3, 4)
        for y in range(-3, 4)
    ]
    assert any(c.green() > 150 and c.green() > c.blue() * 1.1 for c in colors), position


def exercise(controller, renderer, app):
    target = controller.run("construction.point.create", dict(position=[0.3, 0.2, 0.2]))
    controller.select("")
    image = frames(controller, renderer, app)
    output = Path("build/022-points")
    output.mkdir(parents=True, exist_ok=True)
    image.save(str(output / "point-gpu.png"))
    marker(renderer, image, [0.3, 0.2, 0.2])
    assert controller.pick([0.3, 0.2, 3], [0, 0, -1], 0, False, 0.03)["id"] == target


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
        print("GPU texture-only Point marker rendering and matching native picking passed.")
