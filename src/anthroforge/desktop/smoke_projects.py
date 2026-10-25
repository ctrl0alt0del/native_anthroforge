"""Bounded packaged autosave probe, active only with the explicit recovery smoke panel."""

from PySide6.QtCore import QTimer


def start(controller):
    from .smoke import ready

    if not ready(controller):
        QTimer.singleShot(50, lambda: start(controller))
        return
    session = controller.session
    session.command("preferences.set", autosave_enabled=True)
    session.replace_document(name="Recovery smoke edit")
    saver = controller.project_library.autosave
    saver.poll(session)
    saver.due = 0
    saver.poll(session)
    show_when_saved(controller)


def show_when_saved(controller):
    saver = controller.project_library.autosave
    if saver.job is not None:
        QTimer.singleShot(50, lambda: show_when_saved(controller))
        return
    if saver.last:
        controller.project_library.showRecovery()
