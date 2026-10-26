"""Hidden GPU skin display evidence; never shows a native window."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import fiber, frames, settle

from anthroforge.application import skin_evaluation
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/skin-040/ui")


def setup(controller):
    skin_evaluation.TARGET_RESOLUTION = 24
    path = str(Path("examples/primitives/cube.obj").resolve())
    bone = controller.run("import", dict(path=path, units=1.0))["entity_id"]
    settle(controller)
    fiber(controller, bone, 0.2)
    controller.select(bone)
    controller.frameSelection()
    return bone


def exercise(controller, renderer, app):
    bone = setup(controller)
    assert frames(controller, renderer, app).save(str(OUTPUT / "skin-sources-gpu.png"))
    controller.run("skin.envelope.build", {})
    settle(controller)
    stage = controller.session.document.skin.envelope
    assert stage.asset, controller.session.scheduler.errors
    assert frames(controller, renderer, app).save(str(OUTPUT / "skin-envelope-gpu.png"))
    controller.run("workspace.update", dict(hidden=[bone]))
    settle(controller)
    assert frames(controller, renderer, app).save(str(OUTPUT / "skin-isolated-gpu.png"))
    assert any(row["geometry_asset"] == stage.asset for row in controller.render_model.rows)
    assert not renderer.window.isVisible()


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
    print("Skin source/envelope/isolated views rendered on a hidden GPU texture.")


if __name__ == "__main__":
    main()
