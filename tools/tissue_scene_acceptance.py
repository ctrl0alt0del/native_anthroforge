"""Render tissue to an offscreen GPU texture and verify displayed geometry picking."""

from pathlib import Path

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QGuiApplication.processEvents()


def fiber(controller, bone, y):
    source = controller.run(
        "curve.create",
        dict(points=[dict(position=p) for p in [[-0.4, y, 0.6], [0, y, 0.7], [0.4, y, 0.6]]]),
    )
    settle(controller)
    points = controller.session.document.object(source).points
    controller.createConstruction(
        "fiber.create",
        dict(
            curve=source, bindings=[dict(point=p.id, target=bone) for p in (points[0], points[-1])]
        ),
    )
    settle(controller)
    return controller.selection


def scene(controller):
    path = str(Path("examples/primitives/cube.obj").resolve())
    bone = controller.run("import", dict(path=path, units=1.0))["entity_id"]
    settle(controller)
    sources = [fiber(controller, bone, y) for y in (-0.2, 0.2)]
    controller.createConstruction("surface.create", dict(curves=sources, kind="LOFT"))
    settle(controller)
    source = controller.selection
    target = controller.createConstruction("tissue.create", dict(source=source))
    configure(controller, target)
    return target


def configure(controller, target):
    settle(controller)
    controller.run(
        "tissue.configure", dict(target=target, changes=dict(stacking=False, reverse=True))
    )
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.14)))
    settle(controller)
    controller.frameSelection()


def frames(controller, renderer, app):
    for _ in range(8):
        assert not renderer.window.isVisible()
        app.processEvents()
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        image = renderer.frame()
        controller.frame_presented()
    masks = [o for o in renderer.root.findChildren(QObject) if o.objectName().startswith("mask_")]
    assert len(masks) == len(controller.render_model.rows), (
        len(masks),
        controller.render_model.rows,
    )
    return image


def exercise(controller, renderer, app):
    target = scene(controller)
    image = frames(controller, renderer, app)
    output = Path("build/022-tissue")
    output.mkdir(parents=True, exist_ok=True)
    assert image.save(str(output / "tissue-gpu.png"))
    hovered = controller.pick([0, 0, 2], [0, 0, -1], 0, False, 0.005)
    clicked = controller.pick([0, 0, 2], [0, 0, -1], 0, True, 0.005)
    assert hovered["id"] == clicked["id"] == target, (hovered, clicked)
    assert controller.selectedData["handle"]


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
        print("GPU texture-only tissue rendering and matching hover/click passed.")
