"""Hidden stage evidence renderer uses saved selections and the shared comparison scene."""

from pathlib import Path

from PySide6.QtCore import QSizeF, QUrl
from PySide6.QtQml import QQmlComponent

from anthroforge.application import reconstruction_views


def draw(app, controller, renderer, settings):
    restore(controller, settings)
    definition, item = component(renderer)
    item.setParentItem(renderer.window.contentItem())
    item.setSize(QSizeF(renderer.size))
    renderer.root.setVisible(False)
    from .capture import stage_geometry

    stage_geometry(app, controller, renderer)
    for _ in range(4):
        app.processEvents()
        image = renderer.frame()
        controller.frame_presented()
    return image


def restore(controller, settings):
    data = settings["reconstruction"]
    views = tuple(
        reconstruction_views.capture(controller.session, r["subject"], r["stage"], r["variant"])
        for r in data["selections"]
    )
    scene = controller.reconstruction_compare.scene
    scene.synchronize(views)
    scene.set_sections(data["report"])
    camera = settings["camera"]
    scene.camera, scene.mode = [*camera[:5], camera[6]], data["mode"]
    scene.needs_layout_fit = False
    scene.changed.emit()


def component(renderer):
    path = Path(__file__).parent / "qml/ReconstructionComparisonView.qml"
    component = QQmlComponent(renderer.engine, QUrl.fromLocalFile(str(path)))
    item = component.create()
    if item is None:
        raise ValueError(str([e.toString() for e in component.errors()]))
    return component, item
