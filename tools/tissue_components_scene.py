"""Hidden GPU evidence for tissue parameter controls and field point selection."""

from pathlib import Path

from tissue_scene_acceptance import (
    Controller,
    Offscreen,
    QGuiApplication,
    QQuickStyle,
    frames,
    native_runtime,
    scene,
    settle,
)


def exercise(controller, renderer, app):
    target = scene(controller)
    controller.run("tissue.inflation", dict(target=target, changes=dict(mode="CTRL_POINT")))
    settle(controller)
    controller.authoring.editTissueControl("main", "a")
    assert controller.authoring.selectedPoints
    assert frames(controller, renderer, app).save("build/022-tissue/control-gpu.png")
    controller.run("tissue.field.create", dict(target=target, name="pins"))
    settle(controller)
    controller.authoring.editTissueField("pins")
    controller.authoring.selectComponent(controller.authoring.componentRows[12]["key"], False)
    controller.authoring.assignTissueWeight(0.5)
    settle(controller)
    assert frames(controller, renderer, app).save("build/022-tissue/fields-gpu.png")


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        Path("build/022-tissue").mkdir(exist_ok=True, parents=True)
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
        print("Hidden GPU tissue control and field overlays passed.")
