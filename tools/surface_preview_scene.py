"""Invisible native-rendered closed-loft preview, acceptance and lease lifetime."""

from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from surface_scene_acceptance import frames

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-surface-preview")
COORDINATES = ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))


def sources(controller):
    result = [
        controller.run(
            "curve.create",
            dict(
                engine="POLYLINE",
                closed=True,
                points=[dict(position=[x, y, z]) for x, z in COORDINATES],
            ),
        )
        for y in (-0.3, 0.3)
    ]
    controller.session.wait(5)
    controller.refresh()
    return result


def exercise(controller, renderer, app):
    curves = sources(controller)
    result = controller.run("surface.preview", dict(curves=curves))
    controller.session.wait(5)
    controller.refresh()
    controller.cameraRequested.emit([0, 0, 0, 20, 30, 0, 2.5], True)
    frames(controller, renderer, app).save(str(OUTPUT / "preview.png"))
    row = controller.render_model.active_rows()[0]
    assert row["id"].startswith("preview:") and not row["surface_pickable"]
    assert not controller.pick_ids and not controller.snap_ids
    key = controller.run("surface.preview.accept", dict(token=result["token"]))
    frames(controller, renderer, app).save(str(OUTPUT / "accepted.png"))
    assert controller.render_model.active_rows()[0]["id"] == key
    cancel_preview(controller, renderer, app, key)


def cancel_preview(controller, renderer, app, key):
    controller.run("surface.preview", dict(target=key))
    controller.session.wait(5)
    controller.refresh()
    frames(controller, renderer, app)
    handle = controller.session.surface_preview.asset.mesh.handle
    controller.run("surface.preview.cancel", {})
    frames(controller, renderer, app)
    assert handle not in controller.render_model.leases
    assert [row["id"] for row in controller.render_model.active_rows()] == [key]


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        assert not controller.message, controller.message
        print("Invisible surface preview, acceptance, picking exclusion and disposal passed.")
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
