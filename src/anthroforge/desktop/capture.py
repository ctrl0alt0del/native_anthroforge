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


def capture(project, output, revision, view=None):
    if os.name == "nt":
        os.environ["QT_QPA_PLATFORM"] = "windows"
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        return render(app, project, output, revision, view)


def render(app, project, output, revision, view=None):
    controller, warnings = Controller(), []
    controller.capture_mode = True
    controller.timer.stop()
    renderer = None
    try:
        load_revision(controller, project, revision)
        renderer = Offscreen(controller, warnings)
        settings = json.loads(Path(view).read_text(encoding="utf-8")) if view else None
        image = draw(app, controller, renderer, settings)
        return finish(controller, renderer, image, output, warnings, settings)
    finally:
        if renderer is not None:
            renderer.close()
        controller.close()


def load_revision(controller, project, revision):
    adopt(controller.session, *read_package(Path(project), controller.session.engine))
    if controller.session.document.revision != revision:
        raise ValueError("Requested revision does not match the saved document.")
    controller.refresh()


def draw(app, controller, renderer, settings=None):
    if settings is not None:
        inspection_view(controller, settings)
    controller.fiber_display.prepare_capture()
    stage_geometry(app, controller, renderer)
    if settings is None and controller.rows:
        controller.select(controller.rows[0]["id"])
        controller.frameSelection()
    for _ in range(3):
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def inspection_view(controller, settings):
    from .tissue_inspection_capture import restore

    session = controller.session
    session.active_workspace = settings["workspace"]
    controller.refresh()
    controller.cameraRequested.emit(settings["camera"], settings["orthographic"])
    controller.select(settings["selected"])
    controller.authoring.setEditing(settings["editing"])
    restore(controller, settings.get("tissue"))
    controller.route_inspection.restore(settings.get("route"))
    restore_spatial(controller, settings)


def restore_spatial(controller, settings):
    if settings.get("finding"):
        controller.spatial_evidence.restore(settings["finding"], frozen=True)
    if settings.get("measurements"):
        controller.surface_measurements.restore(settings["measurements"])
    placement = settings.get("placement") or settings.get("binding")
    if placement:
        controller.placement_inspection.restore(placement)
    if settings.get("neighborhood"):
        controller.neighborhood.restore_capture(
            settings["neighborhood"], settings["camera"], settings["orthographic"]
        )


def stage_geometry(app, controller, renderer):
    models = controller.geometry_models()
    while any(model.pending for model in models):
        for model in models:
            model.drain()
        app.processEvents()
        renderer.frame()
        controller.frame_presented()


def finish(controller, renderer, image, output, warnings, settings=None):
    raw = QMetaObject.invokeMethod(renderer.root, "inspectScene", Q_RETURN_ARG(str))
    health = json.loads(raw)
    valid = not warnings and health["finite"] and not image.isNull() and image.save(output)
    metadata = controller.session.describe()
    metadata.update(capture_metadata(renderer, output, health, valid, warnings))
    metadata["inspection_view"] = settings
    Path(output + ".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(
        json.dumps(
            dict(captured=valid, revision=metadata["revision"], image=output, warnings=warnings)
        )
    )
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
