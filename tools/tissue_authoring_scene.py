"""Render qualified authoring changes to hidden textures for shape inspection."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_stacking_scene import Offscreen, capture, prepare, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def grouped(controller, renderer, app):
    first, second = prepare(controller)
    capture(controller, renderer, app, "authoring-stacked", second)
    for target in (first, second):
        controller.run("tissue.configure", dict(target=target, changes=dict(group="Family")))
    capture(controller, renderer, app, "authoring-grouped", second)
    assert not controller.session.document.object(second).stack_plan.providers
    return first, second


def profile(controller, renderer, app, first, second):
    hidden = [key for key in controller.session.document.registry.records if key != first]
    controller.run("workspace.update", dict(hidden=hidden))
    controller.selection_view.select(first)
    controller.run(
        "tissue.inflation", dict(target=first, changes=dict(mode="SECTION_PROFILE", amount=0.12))
    )
    capture(controller, renderer, app, "authoring-profile-before", first)
    controller.run("tissue.profile.scale", dict(target=first, factor=2))
    capture(controller, renderer, app, "authoring-profile-scaled", first)
    envelope(controller, renderer, app, first)


def envelope(controller, renderer, app, first):
    controller.run("tissue.configure", dict(target=first, changes=dict(both_sides=True)))
    controller.run("tissue.side.copy", dict(target=first, source="a", destination="b"))
    settle(controller)
    item = controller.session.document.object(first)
    assert item.parts[0].a == item.parts[0].b and item.result.status == "ready"
    capture(controller, renderer, app, "authoring-copied-envelope", first)


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        Path("build/022-tissue").mkdir(parents=True, exist_ok=True)
        first, second = grouped(controller, renderer, app)
        profile(controller, renderer, app, first, second)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden group, profile and copied envelope geometry/picking checks passed.")
