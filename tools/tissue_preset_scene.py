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
    create = controller.construction_view.createConstruction
    for preset in ("LAYER", "POUCH"):
        target = create("tissue.create", dict(source=source, preset=preset))
        if preset == "POUCH":
            controller.run("tissue.relaxation", dict(target=target, changes=dict(mode="NONE")))
        controller.run("tissue.configure", dict(target=target, changes=dict(reverse=True)))
        if preset == "POUCH":
            pouch(controller, renderer, app, target)
        capture(controller, renderer, app, "preset-" + preset.lower())
        controller.run("object.delete", dict(target=target))
        frames(controller, renderer, app)


def pouch(controller, renderer, app, target):
    settle(controller)
    accepted = controller.session.document.object(target).result.asset
    controller.run("tissue.relaxation", dict(target=target, changes=dict(mode="STATIC_PBD")))
    settle(controller)
    item = controller.session.document.object(target)
    assert item.result.asset == accepted and "self-intersections" in item.intrinsic_result.error
    assert frames(controller, renderer, app).save("build/022-tissue/pouch-rejected-gpu.png")
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.08)))
    controller.run("tissue.relaxation", dict(target=target, changes=dict(sagginess=0.2)))
    settle(controller)


def paths(controller, renderer, app):
    membrane = next(o for o in controller.session.document.objects if isinstance(o, Membrane))
    source = membrane.curves[0].curve
    controller.construction_view.createConstruction(
        "tissue.create", dict(source=source, preset="RIM")
    )
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
