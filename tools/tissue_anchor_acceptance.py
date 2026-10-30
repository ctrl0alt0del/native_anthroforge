"""Explicit tissue surface roles and retained Anchor motion through the real QML inspector."""

from PySide6.QtCore import Q_ARG, QMetaObject, QObject, Qt
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
from tissue_fiber_acceptance import search_preserves_choice
from tissue_relaxation_acceptance import click
from ui_acceptance import find


def inspect(controller, window):
    exercise(controller, window)
    target = controller.selection
    controller.construction_view.createConstruction(
        "construction.point.create", dict(position=[0, 0, 0.8])
    )
    settle(controller)
    choose_final(controller, window, target)
    click(window, "createOrRebindAnchor")
    settle(controller)
    check_motion(controller, target)


def choose_final(controller, window, target):
    rows = controller.construction_view.surfaceRoles()
    choice = next(
        i for i, row in enumerate(rows) if row["id"] == target and row["role"] == "TISSUE_FINAL"
    )
    selector = find(window, "pointAttachmentSurface")
    combo = selector.findChild(QObject, "surfaceRoleChoice")
    combo.setProperty("currentIndex", choice)
    QMetaObject.invokeMethod(combo, "activated", Qt.DirectConnection, Q_ARG(int, choice))
    search_preserves_choice(controller, [combo], target)


def check_motion(controller, target):
    before = controller.session.document.object(controller.selection)
    assert before.binding.reference.target == target
    assert before.binding.reference.role == "TISSUE_FINAL" and before.binding.material_asset
    controller.run("tissue.inflation", dict(target=target, changes=dict(amount=0.1)))
    settle(controller)
    current = controller.session.document.object(before.id)
    assert current.result.status == "ready", current.result.error
    assert current.binding == before.binding


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inspect)
            print("Offscreen tissue final-role Anchor capture and motion passed.")
        finally:
            delete(app)
