"""Hidden GPU preview/replacement checks retain the accepted picking surface."""

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, scene, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def exercise(controller, renderer, app):
    target = scene(controller)
    frames(controller, renderer, app)
    before = controller.session.document
    accepted = controller.selection_view.pick([0, 0, 2], [0, 0, -1], 0, False, 0.005)
    controller.run("tissue.preview", dict(target=target, changes=dict(amount=0.25)))
    settle(controller)
    assert controller.construction_view.tissuePreview["state"] == "ready"
    assert frames(controller, renderer, app).save("build/022-tissue/inflation-preview-gpu.png")
    candidate = next(r for r in controller._render_rows if r["id"].startswith("preview:"))
    assert not candidate["pickable"] and not candidate["surface_pickable"]
    picked = controller.selection_view.pick([0, 0, 2], [0, 0, -1], 0, False, 0.005)
    assert picked == accepted, (picked, accepted)
    cancel(controller, renderer, app, before)


def cancel(controller, renderer, app, before):
    controller.run("tissue.preview.cancel", {})
    settle(controller)
    assert frames(controller, renderer, app).save(
        "build/022-tissue/inflation-preview-cancel-gpu.png"
    )
    assert not any(row["id"].startswith("preview:") for row in controller._render_rows)
    assert controller.session.document == before


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
        print("Hidden GPU inflation preview/cancel and accepted picking passed.")
