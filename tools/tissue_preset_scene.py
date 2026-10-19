"""Inspect actual relaxed preset shapes using a hidden GPU texture."""

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, scene, settle
from tissue_shapes_acceptance import capture

from anthroforge.core.membranes import Membrane
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def membranes(controller, renderer, app):
    original = scene(controller)
    source = controller.session.document.object(original).source
    controller.run("object.delete", dict(target=original))
    for preset in ("LAYER", "POUCH"):
        target = controller.createConstruction("tissue.create", dict(source=source, preset=preset))
        controller.run("tissue.configure", dict(target=target, changes=dict(reverse=True)))
        capture(controller, renderer, app, "preset-" + preset.lower())
        controller.run("object.delete", dict(target=target))
        frames(controller, renderer, app)


def paths(controller, renderer, app):
    membrane = next(o for o in controller.session.document.objects if isinstance(o, Membrane))
    source = membrane.curves[0].curve
    controller.createConstruction("tissue.create", dict(source=source, preset="RIM"))
    capture(controller, renderer, app, "preset-rim")


def gpu(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        membranes(controller, renderer, app)
        paths(controller, renderer, app)
        assert not warnings, warnings
        settle(controller)
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        gpu(app)
        print("Hidden GPU preset shapes passed.")
