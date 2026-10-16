"""Read-only GPU image capture of one exact saved document revision."""

import json
import os
from pathlib import Path

from PySide6.QtCore import Q_RETURN_ARG, QMetaObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.application.projects import adopt
from anthroforge.application.storage import read_package

from .controller import Controller
from .offscreen import Offscreen
from .runtime import native_runtime


def capture(project, output, revision):
    if os.name == "nt":
        os.environ["QT_QPA_PLATFORM"] = "windows"
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        return render(app, project, output, revision)


def render(app, project, output, revision):
    controller, warnings = Controller(), []
    controller.capture_mode = True
    renderer = None
    try:
        load_revision(controller, project, revision)
        renderer = Offscreen(controller, warnings)
        image = draw(app, controller, renderer)
        return finish(controller, renderer, image, output, warnings)
    finally:
        if renderer is not None:
            renderer.close()
        controller.close()


def load_revision(controller, project, revision):
    adopt(controller.session, *read_package(Path(project), controller.session.engine))
    if controller.session.document.revision != revision:
        raise ValueError("Requested revision does not match the saved document.")
    controller.refresh()


def draw(app, controller, renderer):
    while controller.render_model.pending:
        controller.render_model.drain()
        app.processEvents()
    if controller.rows:
        controller.select(controller.rows[0]["id"])
        controller.frameSelection()
    for _ in range(3):
        app.processEvents()
        image = renderer.frame()
    return image


def finish(controller, renderer, image, output, warnings):
    raw = QMetaObject.invokeMethod(renderer.root, "inspectScene", Q_RETURN_ARG(str))
    health = json.loads(raw)
    valid = not warnings and health["finite"] and not image.isNull() and image.save(output)
    metadata = controller.session.describe()
    metadata.update(capture_metadata(renderer, output, health, valid, warnings))
    Path(output + ".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"captured": valid, "revision": metadata["revision"], "image": output}))
    return 0 if valid else 1


def capture_metadata(renderer, output, health, valid, warnings):
    return dict(
        image=str(Path(output).resolve()),
        warnings=warnings,
        captured=valid,
        scene=health,
        renderer="QQuickRenderControl",
        window_visible=renderer.window.isVisible(),
    )
