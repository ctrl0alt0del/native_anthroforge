"""Hidden GPU qualification of smoothing, material crop and empty-result replacement."""

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, scene, settle
from tissue_shapes_acceptance import capture

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def render(controller, renderer, app):
    target = scene(controller)
    controller.run("tissue.configure", dict(target=target, changes=dict(both_sides=True)))
    controller.run("tissue.smoothing", dict(target=target, changes=dict(mode="HEIGHT")))
    capture(controller, renderer, app, "smoothed-envelope")
    controller.run("tissue.crop", dict(target=target, changes=dict(enabled=True)))
    capture(controller, renderer, app, "cropped-envelope")
    controller.run("tissue.crop", dict(target=target, changes=dict(origin=[100, 0, 0])))
    settle(controller)
    frames(controller, renderer, app)
    assert not [r for r in controller.render_model.active_rows() if r["id"] == target]
    controller.run("tissue.crop", dict(target=target, changes=dict(enabled=False)))
    capture(controller, renderer, app, "crop-restored")


def gpu(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        render(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        gpu(app)
        print("Hidden GPU crop, empty replacement and restoration passed.")
