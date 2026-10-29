"""Optional hidden renderer accepts scene layers without inventing document objects."""

import json
import os
from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import QSizeF
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.application import inspection_scene_bundle

from . import reconstruction_capture
from .capture import stage_geometry
from .controller import Controller
from .offscreen import Offscreen
from .runtime import native_runtime


def capture(bundle, output):
    if os.name == "nt":
        os.environ["QT_QPA_PLATFORM"] = "windows"
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        return render(app, Path(bundle), output)


def render(app, bundle, output):
    controller, warnings, renderer = Controller(), [], None
    controller.capture_mode = True
    controller.timer.stop()
    try:
        data, layers = inspection_scene_bundle.read(bundle, controller.session.engine)
        renderer = Offscreen(controller, warnings)
        image = draw(app, controller, renderer, data, layers)
        evidence = displayed(controller, layers, data["view"])
        return finish(renderer, image, output, data, warnings, evidence)
    finally:
        if renderer is not None:
            renderer.close()
        controller.close()


def visible(layer, view):
    if layer.kind == "NONE" or layer.identity in view["hidden"] or layer.category in view["hidden"]:
        return False
    mirror = layer.subject.startswith("mirror/")
    return not (
        (mirror and view["mirrors"] == "Source only")
        or (not mirror and view["mirrors"] == "Mirror only")
    )


def restore(controller, data, layers):
    view, scene = data["view"], controller.reconstruction_compare.scene
    displayed = tuple(layer for layer in layers if visible(layer, view))
    views = tuple(
        SimpleNamespace(layers=tuple(r for r in displayed if r.side == side), stage=side)
        for side in ("before", "after")
    )
    scene.synchronize(views)
    camera = view["camera"]
    scene.camera, scene.mode = [*camera[:5], camera[6]], view["mode"]
    scene.needs_layout_fit = False
    scene.changed.emit()


def draw(app, controller, renderer, data, layers):
    restore(controller, data, layers)
    definition, item = reconstruction_capture.component(renderer)
    item.setParentItem(renderer.window.contentItem())
    item.setSize(QSizeF(renderer.size))
    renderer.root.setVisible(False)
    stage_geometry(app, controller, renderer)
    for _ in range(4):
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def displayed(controller, layers, view):
    scene = controller.reconstruction_compare.scene
    expected = {r.identity for r in layers if visible(r, view)}
    actual = {r["id"] for m in scene.models for r in m.active_rows()}
    return dict(complete=expected == actual, displayed=sorted(actual), camera=scene.camera)


def finish(renderer, image, output, data, warnings, evidence):
    valid = evidence["complete"] and not warnings and not image.isNull() and image.save(output)
    result = dict(
        captured=valid,
        snapshot=data["snapshot"],
        view=data["view"],
        warnings=warnings,
        window_visible=renderer.window.isVisible(),
        renderer="QQuickRenderControl",
        scene=evidence,
    )
    Path(output + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 0 if valid else 1
