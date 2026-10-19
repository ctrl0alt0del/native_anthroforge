"""Full-QML relationship edits use shared operations without desktop input."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from material_pins_acceptance import reveal
from PySide6.QtGui import QFont, QFontDatabase
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    settle,
)
from tissue_relaxation_acceptance import click
from ui_acceptance import find

from tests.test_tissue_stack_workflow import assembly, current


def exercise(controller, window):
    _, provider, target = assembly(controller.session)
    controller.refresh()
    controller.select(target)
    settle(controller)
    click(window, "StackingToggle")
    click(window, "tissueStackChoice_" + provider)
    toggle(controller, window, target)
    reveal(find(window, "tissueStackSave"))
    settle(controller)
    assert window.grabWindow().save(str(Path("build/022-tissue/stacking-inspector.png")))


def toggle(controller, window, target):
    control = find(window, "tissueStackExclude")
    control.setProperty("checked", True)
    click(window, "tissueStackSave")
    settle(controller)
    assert controller.session.document.object(target).stack_relationships[0].excluded
    current(controller.session, target)
    controller.run("undo", {})
    settle(controller)
    assert not controller.session.document.object(target).stack_relationships
    assert controller.session.document.object(target).stack_plan.providers


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(exercise)
            print("Offscreen stacking relationship editing and undo passed.")
        finally:
            delete(app)
