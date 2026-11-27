"""Inspect saved Draft and Final geometry on a hidden GPU texture."""

import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from skin_topology_render import displayed

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def capture(controller, renderer, app, output):
    controller.session.command("open", path=str(output / "pipeline.anthroforgex"))
    controller.session.wait()
    hidden = [row.id for row in controller.session.document.entities]
    controller.session.command("workspace.update", hidden=hidden)
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    for stage in ("ENVELOPE", "FINAL"):
        controller.run("workspace.update", dict(skin_display=stage))
        asset = getattr(controller.session.document.skin, stage.lower()).asset
        image = displayed(controller, renderer, app, asset)
        assert image.save(str(output / (stage.lower() + "-gpu.png")))
    assert not renderer.window.isVisible()


def render(app, output):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        capture(controller, renderer, app, output)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


def main():
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        render(app, Path(sys.argv[1]).resolve())
    print("Saved Draft and Final geometry rendered on a hidden GPU texture.")


if __name__ == "__main__":
    main()
