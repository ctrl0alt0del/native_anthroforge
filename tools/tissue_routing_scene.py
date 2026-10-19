"""Inspect automatic routing around a tissue using a hidden GPU texture."""

from pathlib import Path

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from tissue_scene_acceptance import frames, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def radial(session):
    bone = session.command("import", path="examples/primitives/cube.obj", units=1.0)["entity_id"]
    session.wait()
    point = session.command("construction.point.create", position=[0, 0, 2])
    anchor = session.command("anchor.create", source=point, parent=bone)["object_id"]
    session.wait()
    tissue = session.command("tissue.create", source=anchor, preset="CUSTOM")
    session.command("tissue.inflation", target=tissue, changes=dict(amount=0.3))
    session.wait()
    return tissue


def line(session):
    points = [dict(position=[x, 0, 2]) for x in (-1, 1)]
    key = session.command("curve.create", engine="ROUTED", points=points)
    session.wait()
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return item


def inspect(controller, renderer, app):
    tissue = radial(controller.session)
    routed = line(controller.session)
    settle(controller)
    controller.select(routed.id)
    controller.frameSelection()
    top_view(renderer)
    image = frames(controller, renderer, app)
    output = Path("build/022-tissue/tissue-routing-gpu.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    assert image.save(str(output))
    assert controller.session.document.object(tissue).final_result.status == "ready"


def top_view(renderer):
    QMetaObject.invokeMethod(
        renderer.root, "setView", Qt.DirectConnection, Q_ARG("QVariant", "Top")
    )


def run(app):
    controller, warnings = Controller(), []
    renderer = Offscreen(controller, warnings)
    try:
        inspect(controller, renderer, app)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run(app)
        print("Hidden GPU tissue routing capture saved.")
