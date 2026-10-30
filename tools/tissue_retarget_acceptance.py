"""Full offscreen tissue source selection, review and commit through desktop entry points."""

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    exercise,
    native_runtime,
    profiler_application,
    run,
    settle,
)


def inspect(controller, window):
    exercise(controller, window)
    target = controller.selection
    original = controller.session.document.object(target)
    source = new_anchor(controller)
    controller.selection_view.select(target)
    settle(controller)
    activate(window, "retargetTissueSource")
    settle(controller)
    assert window.property("modalOpen")
    activate(window, "tissueSource_" + source)
    settle(controller)
    assert window.property("modalOpen")
    approve(controller, window, original, source)


def new_anchor(controller):
    parent = controller.session.document.entities[0].id
    point = controller.run("construction.point.create", dict(position=[0, 0, 0.7]))
    result = controller.run("anchor.create", dict(source=point, parent=parent))
    settle(controller)
    return result["object_id"]


def activate(window, name):
    pending = [window.contentItem()]
    while pending:
        button = pending.pop()
        if button.objectName() == name and button.property("visible"):
            assert button.property("enabled")
            assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
            return
        pending.extend(button.childItems())
    raise AssertionError(name)


def approve(controller, window, original, source):
    cursor = controller.session.history.cursor
    activate(window, "approveReplacementChanges")
    activate(window, "applyReplacement")
    settle(controller)
    assert not window.property("modalOpen")
    current = controller.session.document.object(original.id)
    assert current.source == source and current.result.status == "ready", current.result.error
    assert current.classification == original.classification
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert controller.session.document.object(original.id).source == original.source


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen tissue retarget: source picker, review, apply and undo passed.")
        finally:
            delete(app)
