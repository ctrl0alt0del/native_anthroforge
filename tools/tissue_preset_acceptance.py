"""Use the desktop preset chooser without a visible window or desktop input."""

from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    scene,
    settle,
)
from tissue_relaxation_acceptance import click
from ui_acceptance import find


def inspect(controller, window):
    scene(controller)
    source = controller.selection
    for index, name in ((2, "LAYER"), (3, "POUCH")):
        controller.select(source)
        settle(controller)
        find(window, "tissueCreationPreset").setProperty("currentIndex", index)
        click(window, "createTissue")
        settle(controller)
        item = controller.session.document.object(controller.selection)
        assert item.preset == name and item.result.status == "ready", item.result.error
        assert find(window, "tissueClassification").property("text") == "SOFT_TISSUE"
    independent(controller, window)


def independent(controller, window):
    target = controller.selection
    original = controller.session.document.object(target).source
    click(window, "tissueMakeIndependent")
    settle(controller)
    item = controller.session.document.object(target)
    assert item.source != original and item.result.status == "ready"
    controller.run("undo", {})
    settle(controller)
    assert controller.session.document.object(target).source == original


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen Layer/Pouch preset creation passed.")
        finally:
            delete(app)
