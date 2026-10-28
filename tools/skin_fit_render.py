"""Hidden GPU verification of staged fitted-skin playback, without a visible window."""

import os
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from skin_qualification_scene import setup
from tissue_scene_acceptance import frames

from anthroforge.desktop import offscreen, runtime
from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/skin-040/ui").resolve()


def fixture(controller):
    identity = setup(controller.session)
    controller.run(
        "skin.fit",
        dict(shortcut=identity, settings=dict(minimum=0, maximum=0.2, bones=1, samples=5)),
    )
    controller.session.wait()
    controller.run("view.hide", dict(targets=[controller.session.document.entities[0].id]))
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    return controller.session.document.skin.fits[-1]


def snapshot(controller, renderer, application, name):
    for _ in range(30):
        controller.process_tick()
        image = frames(controller, renderer, application)
        QTest.qWait(10)
    assert image.save(str(OUTPUT / (name + ".png")))
    assert image.pixelColor(640, 560).lightness() > 80, "No skin pixels in the hidden GPU view."
    return controller.render_model.active_rows()


def exercise(controller, renderer, application):
    item = fixture(controller)
    snapshot(controller, renderer, application, "skin-reference-gpu")
    controller.run("skin.fit.preview", dict(identity=item.id, value=0.15))
    controller.session.wait()
    controller.refresh()
    rows = snapshot(controller, renderer, application, "skin-fit-gpu")
    candidate = controller.session.skin_fit_preview.asset
    assert any(row["handle"] == candidate.mesh.handle for row in rows)
    assert not controller.render_model.pending
    controller.run("skin.fit.preview.cancel", {})
    rows = snapshot(controller, renderer, application, "skin-preview-hidden-gpu")
    assert all(row["handle"] != candidate.mesh.handle for row in rows)


def run(application):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = offscreen.Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, application)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    native = os.environ.get("AF_SKIN_BUILD")
    if native:
        runtime.build_directory = lambda: Path(native)
        offscreen.build_directory = runtime.build_directory
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    with runtime.native_runtime():
        run(application)


if __name__ == "__main__":
    main()
