"""Inspect tissue on the provenance-backed skull routing fixture using hidden GPU frames."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from skull_construction_fixture import create
from tissue_scene_acceptance import frames, settle

from anthroforge.core.membranes import Membrane
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/022-tissue/skull")


def assembly(controller):
    create(controller.session, OUTPUT)
    membrane = next(o for o in controller.session.document.objects if isinstance(o, Membrane))
    target = controller.createConstruction(
        "tissue.create", dict(source=membrane.id, name="Skull fixture tissue")
    )
    controller.run("tissue.configure", dict(target=target, changes=dict(stacking=False)))
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.04)))
    settle(controller)
    assert controller.session.document.object(target).result.status == "ready"
    return target


def capture(controller, renderer, app):
    target = assembly(controller)
    controller.select(target)
    for name, angles in (("front", (0, 0)), ("oblique", (-10, 30)), ("side", (0, 75))):
        controller.cameraRequested.emit([0.15, -0.45, 1.35, *angles, 0, 3], True)
        assert frames(controller, renderer, app).save(str(OUTPUT / (name + ".png")))
    controller.session.command(
        "save", path=str(OUTPUT / "skull-tissue.anthroforge"), blocked_policy="wait"
    )


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        capture(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden skull fixture tissue construction and save passed.")
