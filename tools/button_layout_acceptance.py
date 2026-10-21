"""Check naturally sized action labels with hidden GPU rendering and Windows font metrics."""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "windows" if os.name == "nt" else "offscreen"

from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from ui_polish_acceptance import descendants

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/tissue-intersection-policy/ui")


def verify(renderer):
    rows = [
        node
        for node in descendants(renderer.root)
        if node.isVisible() and node.metaObject().indexOfProperty("truncated") >= 0
    ]
    clipped = [node.property("text") for node in rows if node.property("truncated")]
    assert rows and not clipped, clipped
    assert not renderer.window.isVisible()


def check(app, family):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = Offscreen(controller, warnings)
    try:
        for _ in range(3):
            app.processEvents()
            image = renderer.frame()
        verify(renderer)
        assert not warnings, warnings
        assert image.save(str(OUTPUT / (family + "-buttons.png")))
    finally:
        renderer.close()
        controller.close()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        check(app, "platform-default")
        for family in ("Segoe UI", "Arial", "Tahoma"):
            app.setFont(QFont(family))
            check(app, family)
    print("Hidden GPU action labels fit natural button widths across four font configurations.")


if __name__ == "__main__":
    main()
