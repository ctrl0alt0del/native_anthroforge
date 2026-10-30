"""Exercise role-aware Fiber capture from a tissue through the actual QML controls."""

from PySide6.QtCore import Q_ARG, QMetaObject, Qt
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
from tissue_relaxation_acceptance import click


def inspect(controller, window):
    exercise(controller, window)
    target = controller.selection
    source = controller.run(
        "curve.create", dict(points=[dict(position=[x, 0.2, 0.8]) for x in (-0.3, 0, 0.3)])
    )
    settle(controller)
    controller.selection_view.select(source)
    controller.authoring.setEditing(True)
    settle(controller)
    choose_surfaces(controller, window, source, target)
    click(window, "createFiberFromCurve")
    settle(controller)
    verify(controller, target)


def choose_surfaces(controller, window, source, target):
    click(window, "Fiber binding optionsToggle")
    settle(controller)
    rows = controller.construction_view.surfaceRoles()
    index = next(
        i for i, row in enumerate(rows) if row["id"] == target and row["role"] == "TISSUE_FINAL"
    )
    choices = surface_choices(window, source)
    assert choices
    for choice in choices:
        choice.setProperty("currentIndex", index + 1)
        QMetaObject.invokeMethod(choice, "activated", Qt.DirectConnection, Q_ARG(int, index + 1))
    search_preserves_choice(controller, choices, target)


def search_preserves_choice(controller, choices, target):
    for choice in choices:
        chooser = choice.parentItem()
        search = next(
            item
            for item in chooser.childItems()
            if item.property("placeholderText") == "Search anatomical surfaces"
        )
        search.setProperty("text", "No matching surfaces")
        settle(controller)
        current = chooser.property("current")
        assert (current.toVariant() if hasattr(current, "toVariant") else current)["id"] == target


def surface_choices(window, source):
    pending, result = [window.contentItem()], []
    while pending:
        item = pending.pop()
        if item.objectName() == "surfaceRoleChoice":
            parent = item.parentItem()
            if (
                parent.objectName() == "fiberCreationSurface"
                and parent.property("sourceId") == source
            ):
                result.append(item)
        pending.extend(item.childItems())
    return result


def verify(controller, target):
    item = controller.session.document.object(controller.selection)
    assert item.bindings and not controller.authoring.active
    assert all(b.target == target and b.role == "TISSUE_FINAL" for b in item.bindings)
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.1)))
    settle(controller)
    changed = controller.session.document.object(item.id)
    assert changed.result.status == "ready", changed.result.error
    assert changed.bindings == item.bindings


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen tissue final-role Fiber creation and propagation passed.")
        finally:
            delete(app)
