"""Exercise part, side, profile and control editing without desktop input."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
from tissue_relaxation_acceptance import argument, click
from ui_acceptance import find

from tests.test_tissue_parts_workflow import branched_tissue


def activate(window, name, index):
    combo = find(window, name)
    combo.setProperty("currentIndex", index)
    assert QMetaObject.invokeMethod(combo, "activated", Qt.DirectConnection, argument(index))


def profile(controller, window):
    exercise(controller, window)
    target = controller.selection
    modes = controller.selectedData["tissue_modes"]
    activate(window, "tissueInflationMode", modes.index("SECTION_PROFILE"))
    settle(controller)
    assert controller.session.document.object(target).parts[0].a.inflation.profile.initialized
    activate(window, "tissueProfileDirection", 2)
    click(window, "tissueProfileReset")
    settle(controller)
    item = controller.session.document.object(target)
    assert item.parts[0].a.inflation.profile.direction == "SMOOTH"


def enable_envelope(window):
    find(window, "tissueBothSides").setProperty("checked", True)
    click(window, "tissueBothSides")


def select_control(controller, window):
    modes = controller.selectedData["tissue_modes"]
    activate(window, "tissueInflationMode", modes.index("CTRL_POINT"))


def smoothing(controller, window):
    exercise(controller, window)
    click(window, "InflationToggle")
    click(window, "Height smoothingToggle")
    activate(window, "tissueSmoothingMode", 1)
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert item.parts[0].a.smoothing.mode == "HEIGHT"
    assert item.result.status == "ready" and item.diagnostics[0].pinned > 0


def branch(controller, window):
    _, target, identity = branched_tissue(controller.session)
    controller.refresh()
    controller.select(target)
    settle(controller)
    activate(window, "tissuePart", 1)
    enable_envelope(window)
    settle(controller)
    activate(window, "tissueSide", 1)
    select_control(controller, window)
    click(window, "tissueControlReset")
    settle(controller)
    part = controller.session.document.object(target).parts[1]
    assert part.id == identity and len(part.b.inflation.control) == 3
    manipulate(controller, window, identity)


def manipulate(controller, window, identity):
    assert controller.session.document.object(controller.selection).both_sides
    click(window, "tissueControlManipulate")
    assert controller.authoring.selectedComponent["side"] == "b"
    assert controller.authoring.selectedComponent["piece"] == identity


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(profile)
            run(branch)
            run(smoothing)
            print("Offscreen profile, branch and independent side editing passed.")
        finally:
            delete(app)
