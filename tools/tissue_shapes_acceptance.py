"""Hidden GPU inspection of radial, sweep and normal-shell desktop outputs."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import fiber, frames, scene, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def capture(controller, renderer, app, name):
    settle(controller)
    assert controller.selection_view.selectedData["status"] == "ready", (
        controller.session.scheduler.errors
    )
    assert (
        controller.selection_view.selectedData["is_tissue"]
        and not controller.selection_view.selectedData["transformable"]
    )
    controller.viewport_view.frameSelection()
    output = Path("build/022-tissue")
    output.mkdir(parents=True, exist_ok=True)
    assert frames(controller, renderer, app).save(str(output / (name + "-gpu.png")))


def shell(controller, renderer, app):
    target = scene(controller)
    controller.run(
        "tissue.inflation", dict(target=target, changes=dict(mode="NORMAL", minimum=0.015))
    )
    capture(controller, renderer, app, "normal-shell")
    controller.run("object.delete", dict(target=target))
    frames(controller, renderer, app)


def sweep(controller, renderer, app):
    bone = controller.session.document.entities[0].id
    source = fiber(controller, bone, 0)
    target = controller.construction_view.createConstruction(
        "tissue.create", dict(source=source, preset="CUSTOM")
    )
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.15, width=0.12)))
    capture(controller, renderer, app, "profile-sweep")
    controller.run("object.delete", dict(target=target))


def radial(controller, renderer, app):
    bone = controller.session.document.entities[0].id
    point = controller.run("construction.point.create", dict(position=[0, 0, 0.7]))
    controller.construction_view.createConstruction(
        "anchor.create", dict(source=point, parent=bone)
    )
    settle(controller)
    target = controller.construction_view.createConstruction(
        "tissue.create", dict(source=controller.selection, preset="CUSTOM")
    )
    controller.run(
        "tissue.inflation", dict(target=target, changes=dict(amount=0.2, scale=[1.4, 0.7, 1]))
    )
    capture(controller, renderer, app, "radial")


def replacement_cycles(controller, renderer, app):
    source = controller.session.document.object(controller.selection).source
    for index in range(12):
        old = controller.selection
        controller.run("object.delete", dict(target=old))
        target = controller.construction_view.createConstruction(
            "tissue.create", dict(source=source, preset="CUSTOM")
        )
        controller.run(
            "tissue.inflation", dict(target=target, changes=dict(amount=0.15 + index * 0.005))
        )
        settle(controller)
        frames(controller, renderer, app)
        assert controller.selection_view.selectedData["status"] == "ready"


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        for operation in (shell, sweep, radial):
            operation(controller, renderer, app)
        replacement_cycles(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden GPU radial, profile sweep and normal-shell outputs passed.")
