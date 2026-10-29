"""Hidden reconstruction navigation qualification; no desktop input or visible windows."""

import json
import os
from pathlib import Path

from PySide6.QtCore import QSizeF, QUrl
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.desktop import offscreen, runtime
from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/reconstruction-042/gui")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(OUTPUT / "preferences.json")
    build = Path(os.environ.get("AF_NATIVE_BUILD", "build/dev")).resolve()
    runtime.build_directory = offscreen.build_directory = lambda: build
    app = QGuiApplication([])
    QQuickStyle.setStyle("Basic")
    with runtime.native_runtime():
        run(app)


def run(app):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = offscreen.Offscreen(controller, warnings)
    renderer.window.setColor(QColor("#2b2c30"))
    try:
        fixture(controller)
        panel(app, controller, renderer)
        review(app, controller, renderer)
        assert not renderer.window.isVisible() and not warnings, warnings
        (OUTPUT / "result.json").write_text(json.dumps(dict(warnings=warnings, visible=False)))
    finally:
        renderer.close()
        controller.close()


def fixture(controller):
    session = controller.session
    target = session.command("import", path="examples/primitives/cube.obj", units=1)["entity_id"]
    session.wait()
    controller.refresh()
    controller.select(target)
    controller.reconstruction_panel.create()
    controller.reconstruction_panel.run("variant.checkpoint", {"name": "Initial alternative"})


def panel(app, controller, renderer):
    path = Path("src/anthroforge/desktop/qml/ReconstructionPane.qml").resolve()
    component = QQmlComponent(renderer.engine, QUrl.fromLocalFile(str(path)))
    item = component.create()
    assert item is not None, [e.toString() for e in component.errors()]
    renderer.root.setVisible(False)
    item.setParentItem(renderer.window.contentItem())
    item.setSize(QSizeF(360, 960))
    for _ in range(5):
        app.processEvents()
        image = renderer.frame()
    assert image.save(str(OUTPUT / "variants.png"))
    item.deleteLater()


def review(app, controller, renderer):
    key = controller.session.contexts.visible
    controller.variant_panel.inspect(key, "promote")
    controller.session.variant_review.wait(60)
    controller.variant_panel.synchronize()
    path = review_wrapper()
    component = QQmlComponent(renderer.engine, QUrl.fromLocalFile(str(path)))
    item = component.create()
    assert item is not None, [e.toString() for e in component.errors()]
    render_review(app, controller, renderer, item)


def review_wrapper():
    path = (OUTPUT / "Review.qml").resolve()
    qml = Path("src/anthroforge/desktop/qml").resolve().as_uri()
    body = "Item { VariantReviewDialog { Component.onCompleted: open() } }"
    path.write_text('import QtQuick\nimport "' + qml + '"\n' + body)
    return path


def render_review(app, controller, renderer, item):
    item.setSize(QSizeF(1280, 960))
    item.setParentItem(renderer.window.contentItem())
    for _ in range(12):
        app.processEvents()
        controller.process_tick()
        image = renderer.frame()
        controller.frame_presented()
    assert image.save(str(OUTPUT / "promotion.png"))
    item.deleteLater()


if __name__ == "__main__":
    main()
