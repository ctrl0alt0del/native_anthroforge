"""Render saved topology results on a hidden GPU texture, with no desktop interaction."""

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from tissue_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def capture(controller, renderer, app, output, backend):
    controller.run("open", dict(path=str(output / f"{backend}.anthroforge")))
    controller.session.wait()
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    for stage in ("ENVELOPE", "TOPOLOGY"):
        if not getattr(controller.session.document.skin, stage.lower()).asset:
            continue
        controller.run("workspace.update", dict(skin_display=stage))
        controller.refresh()
        asset = getattr(controller.session.document.skin, stage.lower()).asset
        image = displayed(controller, renderer, app, asset)
        assert image.save(str(output / f"{backend}-{stage}-gpu.png"))


def displayed(controller, renderer, app, asset):
    for _ in range(200):
        QTest.qWait(20)
        image = frames(controller, renderer, app)
        if any(row["geometry_asset"] == asset for row in controller.render_model.active_rows()):
            return image
    raise AssertionError("The complete accepted skin revision was not displayed.")


def render(app, output, backends):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        for backend in backends:
            capture(controller, renderer, app, output, backend)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


def main():
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        render(app, Path(sys.argv[1]).resolve(), sys.argv[2:] or ("INSTANT", "QUADWILD"))
    print("Reopened topology and envelope results rendered without visible windows.")


if __name__ == "__main__":
    main()
