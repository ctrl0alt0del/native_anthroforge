"""Texture-only surface rendering, staged replacement and displayed-revision picking."""

import json
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.core.surfaces import Surface
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/020-surface-scene")


def frames(controller, renderer, app, count=4):
    for _ in range(count):
        assert not renderer.window.isVisible()
        controller.render_model.drain()
        controller.path_model.drain()
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def fixture(controller):
    keys = [
        controller.run("curve.create", dict(points=[dict(position=[x, 0, z]) for x in (-0.6, 0.6)]))
        for z in (-0.3, 0.3)
    ]
    controller.run("surface.create", dict(curves=keys, name="Shared curve loft"))
    controller.session.wait(5)
    target = next(o.id for o in controller.session.document.objects if isinstance(o, Surface))
    controller.refresh()
    controller.selection_view.select(target)
    controller.cameraRequested.emit([0, 0, 0, 0, 0, 0, 2.5], True)
    return target, keys


def pick(controller, target):
    hit = controller.selection_view.pick([0, -2, 0], [0, 1, 0], 0, False, 0.02)
    assert hit.get("id") == target, (
        hit,
        controller.pick_ids,
        controller.render_model.active_rows(),
    )
    assert controller.selection_view.pick([0, -2, 0], [0, 1, 0], 0, True, 0.02) == hit
    assert target not in controller.snap_ids


def replacement(controller, renderer, app, target, source):
    before = controller.render_model.active_rows()[0]
    edit_source(controller, source)
    assert controller.render_model.active_rows()[0]["handle"] == before["handle"]
    assert controller.render_model.leases[before["handle"]]
    pick(controller, target)
    frames(controller, renderer, app).save(str(OUTPUT / "edited-loft.png"))
    current = controller.render_model.active_rows()[0]
    assert current["handle"] != before["handle"]
    assert controller.pick_handles.tolist() == [current["handle"]]
    assert before["handle"] not in controller.render_model.leases
    pick(controller, target)


def edit_source(controller, source):
    item = controller.session.document.object(source)
    controller.run(
        "curve.point.update", dict(curve=source, point=item.points[0].id, position=[-0.6, 0, 0.6])
    )
    controller.session.wait(5)
    controller.refresh()


def exercise(controller, renderer, app):
    target, sources = fixture(controller)
    image = frames(controller, renderer, app)
    assert image.save(str(OUTPUT / "loft.png"))
    row = controller.render_model.active_rows()[0]
    assert row["id"] == target and row["geometry_revision"] > 0
    pick(controller, target)
    replacement(controller, renderer, app, target, sources[1])


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        report()
    finally:
        renderer.close()
        controller.close()


def report():
    result = dict(
        passed=True,
        renderer="QQuickRenderControl/D3D11",
        visible_window=False,
        picking="displayed revision; hover/click agreement",
        replacement="old mesh retained",
        anatomical_snapping="surface excluded",
    )
    (OUTPUT / "acceptance.json").write_text(json.dumps(result))
    print(json.dumps(result))


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
