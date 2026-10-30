"""Exercise the actual branch inspector without a visible native window."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from branch_scene_fixture import create
from fiber_editor_acceptance import settle
from junction_editor_acceptance import click
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime


def controls(controller, window):
    keys, target = create(controller.session)
    settle(controller)
    controller.selection_view.select(target)
    settle(controller)
    click(controller, window, "BranchesToggle")
    for index in range(2):
        check = find(window, "branchSource" + str(index))
        check.setProperty("checked", True)
        click(controller, window, check.objectName())
    click(controller, window, "addSurfaceBranch")
    assert controller.session.document.object(target).kind == "BRANCHED", controller.message
    check_removal(controller, window, target)


def check_removal(controller, window, target):
    click(controller, window, "removeSurfaceBranch0")
    assert controller.session.document.object(target).kind == "LOFT", controller.message
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(target).kind == "BRANCHED"
    click(controller, window, "surfaceIndependent0")
    assert controller.session.document.object(target).result.status == "ready", controller.message


def run():
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        window.hide()
        controls(controller, window)
        assert not warnings, warnings
        print("Offscreen branch add/remove, undo and assembly independence passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
