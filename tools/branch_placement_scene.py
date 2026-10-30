"""Actual new branch workflow rendered by hidden QQuickRenderControl, with membrane parity."""

import json
from pathlib import Path

import numpy as np
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from surface_scene_acceptance import frames

from anthroforge.core.surfaces import Surface
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/branched-point-placement")


def curves(session):
    case = json.loads(Path("tests/fixtures/surfaces/branches.json").read_text())["cases"][0]
    keys = [
        session.command("curve.create", points=[dict(position=p) for p in row], engine="POLYLINE")
        for row in case["rows"][:2]
    ]
    for index, row in enumerate(case["rows"][2:], 1):
        keys.append(branch(session, keys[0], index, row))
    session.wait()
    return keys


def branch(session, source, index, row):
    root = session.document.object(source).points[index]
    return session.command(
        "curve.branch.create",
        source=dict(curve=source, point=root.id),
        points=[dict(position=p) for p in row],
        engine="POLYLINE",
    )


def fixture(controller):
    session = controller.session
    keys = curves(session)
    controller.refresh()
    return selected_surface(controller, keys)


def selected_surface(controller, keys):
    session = controller.session
    for index, key in enumerate(keys):
        controller.selection_view.select(key, index > 0)
    controller.construction_view.createSurface("AUTO")
    session.wait()
    controller.refresh()
    surfaces = [o for o in session.document.objects if isinstance(o, Surface)]
    assert surfaces, controller.message
    item = surfaces[-1]
    assert item.kind == "BRANCHED" and item.result.status == "ready"
    controller.selection_view.select(item.id)
    controller.cameraRequested.emit([0.5, -0.1, 0.1, -65, 15, 0, 2.1], True)
    return item


def membrane(controller, surface):
    session = controller.session
    cube = str(Path("examples/primitives/cube.obj").resolve())
    bone = session.command("import", path=cube, units=1.0)["entity_id"]
    session.wait()
    job = session.command("membrane.create", source=surface.id)
    session.wait()
    item = session.document.object(job["object_id"])
    same_geometry(session, item, surface)
    hidden = [bone, surface.id, *(u.curve for u in surface.curves)]
    session.command("workspace.update", hidden=hidden)
    controller.refresh()
    controller.selection_view.select(item.id)
    return item


def same_geometry(session, first, second):
    np.testing.assert_allclose(
        session.assets[first.result.asset].mesh.array(0),
        session.assets[second.result.asset].mesh.array(0),
        atol=1e-12,
    )


def exercise(controller, renderer, app):
    surface = fixture(controller)
    assert frames(controller, renderer, app).save(str(OUTPUT / "automatic-branch-gpu.png"))
    root_preview(controller, renderer, app)
    item = membrane(controller, surface)
    assert frames(controller, renderer, app).save(str(OUTPUT / "membrane-gpu.png"))
    controller.session.command(
        "save", path=str(OUTPUT / "branched-membrane.anthroforge"), blocked_policy="wait"
    )
    controller.session.wait()
    assert item.kind == "BRANCHED"


def root_preview(controller, renderer, app):
    tool = controller.drawing_tools
    tool.begin("BRANCH")
    tool.pointer([0.21, 0, 3, 0, 0, -1, 500, 500, 1], [0, 0, -1], False)
    np.testing.assert_allclose(tool.hover, [0.2, 0, 0])
    assert frames(controller, renderer, app).save(str(OUTPUT / "root-preview-gpu.png"))
    tool.cancel()


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        exercise(controller, renderer, app)
        assert not warnings, warnings
        print("Hidden GPU branch and membrane renders, shape parity and saving passed.")
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
