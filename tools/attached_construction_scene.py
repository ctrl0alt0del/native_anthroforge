"""Hidden GPU evidence for automatic attached construction; never shows a native window."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import configure, frames, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime
from tests.test_attached_creation import surface_scene

OUTPUT = Path("build/direct-tissue-stable-inspectors")


def scene(controller):
    _, source, _ = surface_scene(controller.session)
    controller.refresh()
    controller.selection_view.select(source.id)
    create = controller.construction_view.createConstruction
    result = create("tissue.create", dict(source=source.id))
    settle(controller)
    target = result["object_id"]
    assert controller.selection == target
    configure(controller, target)
    controller.run(
        "save", dict(path=str(OUTPUT / "automatic-tissue.anthroforge"), blocked_policy="wait")
    )
    settle(controller)
    return target


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        target = scene(controller)
        image = frames(controller, renderer, app)
        assert image.save(str(OUTPUT / "automatic-tissue-gpu.png"))
        assert controller.session.document.object(target).final_result.status == "ready"
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
    print("Automatic Surface / Membrane / Tissue saved and rendered with a hidden GPU target.")


if __name__ == "__main__":
    main()
