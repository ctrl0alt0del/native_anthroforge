"""Use the desktop preset chooser without a visible window or desktop input."""

from PySide6.QtCore import QMetaObject, Qt
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
from tissue_relaxation_acceptance import argument, click
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
        assert item.preset == name
        qualify(controller, item)
        assert find(window, "tissueClassification").property("text") == "SOFT_TISSUE"
    apply_existing(controller, window)
    independent(controller, window)


def apply_existing(controller, window):
    target = controller.selection
    before = controller.session.document.object(target)
    cursor = controller.session.history.cursor
    click(window, "Apply presetToggle")
    combo = find(window, "tissueApplyPreset")
    combo.setProperty("currentIndex", 1)
    assert QMetaObject.invokeMethod(combo, "activated", Qt.DirectConnection, argument(1))
    settle(controller)
    item = controller.session.document.object(target)
    assert item.preset == "CUSTOM" and item.source == before.source
    assert item.classification == before.classification and item.stacking == before.stacking
    assert controller.session.history.cursor == cursor + 1


def qualify(controller, item):
    if item.preset == "POUCH" and item.result.status == "failed":
        assert "self-intersections" in item.intrinsic_result.error
        controller.run("tissue.inflation", dict(target=item.id, changes=dict(amount=0.08)))
        controller.run("tissue.relaxation", dict(target=item.id, changes=dict(sagginess=0.2)))
        settle(controller)
    current = controller.session.document.object(item.id)
    assert current.result.status == "ready", current.result.error


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
