"""Background native renderer acceptance for historical shortcut geometry."""

from dataclasses import asdict
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shortcut_inspection_acceptance import anchor_fixture
from shortcuts_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/shortcut-comparison-review")


def capture(controller, renderer, application, name):
    image = frames(controller, renderer, application)
    assert image.save(str(OUTPUT / (name + ".png")))
    return image


def exercise(controller, renderer, application):
    key = anchor_fixture(controller)
    tool = controller.shortcut_comparison
    tool.capture(key)
    baseline = capture(controller, renderer, application, "baseline")
    edit(controller, key, 2)
    controller.session.wait(10)
    after = capture(controller, renderer, application, "after")
    assert baseline != after
    modes(controller, renderer, application, key)


def modes(controller, renderer, application, key):
    tool = controller.shortcut_comparison
    tool.setMode("Before")
    capture(controller, renderer, application, "before")
    assert tool.before and tool.model.active_rows()
    edit(controller, key, 1.8)
    assert not tool.before
    controller.session.wait(10)
    tool.setMode("Overlay")
    capture(controller, renderer, application, "overlay")
    assert tool.model.leases
    tool.clear()
    capture(controller, renderer, application, "cleared")
    assert not tool.model.leases


def edit(controller, key, value):
    ref = next(s.reference for s in controller.session.document.shortcuts if s.id == key)
    controller.run("shortcut.set", dict(reference=asdict(ref), value=value))
    assert controller.session.document.entity(ref.target).matrix[0] == value


def run(application):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, application)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    with native_runtime():
        run(application)
