"""Initial camera/selection restoration after asynchronous project adoption."""

from PySide6.QtCore import QTimer


def prepare(controller, project):
    controller.viewport_view.camera_workspace = None
    controller.viewport_view.restore_camera()
    if project and controller.session.document.entities:
        controller.selection_view.select(controller.session.document.entities[0].id)
        if controller.session.workspace.camera == (0.0, 0.0, 0.0, -20.0, 25.0, 0.0, 4.0):
            QTimer.singleShot(100, controller.viewport_view.frameSelection)


def adopted(controller):
    if getattr(controller, "initial_project", False):
        controller.initial_project = False
        prepare(controller, True)
