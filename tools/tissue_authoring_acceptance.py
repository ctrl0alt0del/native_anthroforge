"""Actual inspector edits through offscreen Qt controls, without desktop interaction."""

from pathlib import Path

from numeric_input_acceptance import drag, find, reveal, type_value
from PySide6.QtCore import QMetaObject, QPoint, QPointF, Qt
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
from tissue_parts_acceptance import activate, enable_envelope
from tissue_relaxation_acceptance import click

OUTPUT = Path("build/tissue-authoring-controls")


def capture(window, name):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def inflation(controller, window):
    exercise(controller, window)
    target = controller.selection
    type_value(window, "tissueBoundaryPowerValue", "2.5")
    settle(controller)
    assert controller.session.document.object(target).parts[0].a.inflation.boundary_power == 2.5
    field = find(window, "tissueBoundaryPowerValue")
    before, cursor = controller.session.document.object(target), controller.session.history.cursor
    drag(window, field, 25)
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert controller.session.document.object(target).parts == before.parts
    capture(window, "boundary-power")
    copy_side(controller, window, target)


def copy_side(controller, window, target):
    enable_envelope(window)
    settle(controller)
    reveal(window, "tissueCopyAToB")
    click(window, "tissueCopyAToB")
    settle(controller)
    part = controller.session.document.object(target).parts[0]
    assert part.a == part.b
    capture(window, "side-copy-boundary")
    controller.run("undo", {})
    settle(controller)
    part = controller.session.document.object(target).parts[0]
    assert part.a != part.b


def stacking(controller, window):
    exercise(controller, window)
    click(window, "StackingToggle")
    click(window, "Stacking settingsToggle")
    field = find(window, "tissueStackGroup")
    field.setProperty("text", "Front")
    assert QMetaObject.invokeMethod(field, "editingFinished", Qt.DirectConnection)
    type_value(window, "tissueStackAllowanceValue", "0.25")
    settle(controller)
    item = controller.session.document.object(controller.selection)
    assert item.group == "Front" and item.stack_settings.displacement == 0.25
    reveal(window, "tissueStackGroup")
    capture(window, "stacking-controls")


def profile_value(controller):
    return controller.session.document.object(controller.selection).parts[0].a.inflation.profile


def profile(controller, window):
    exercise(controller, window)
    modes = controller.selectedData["tissue_modes"]
    activate(window, "tissueInflationMode", modes.index("SECTION_PROFILE"))
    settle(controller)
    type_value(window, "tissueProfileDepthValue", "0.04")
    settle(controller)
    assert profile_value(controller).depths == (0.02, 0.04, 0.04, 0.02), (
        profile_value(controller),
        controller.message,
    )
    profile_drag(controller, window)
    profile_preview(controller, window)


def profile_drag(controller, window):
    reveal(window, "tissueProfileDepthValue")
    field = find(window, "tissueProfileDepthValue")
    before, cursor = profile_value(controller), controller.session.history.cursor
    drag(window, field, 25)
    after = profile_value(controller)
    assert_depths(after.depths, (0.02125, 0.0425, 0.0425, 0.02125))
    assert after.peaks == before.peaks and controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    settle(controller)
    drag(window, field, 25, cancel=True)
    assert profile_value(controller) == before
    zero_drag(controller, window, field)
    capture(window, "profile-scaling")


def zero_drag(controller, window, field):
    from PySide6.QtTest import QTest

    before, cursor = profile_value(controller), controller.session.history.cursor
    start = field.mapToScene(QPointF(field.width() / 2, field.height() / 2)).toPoint()
    QTest.mousePress(window, Qt.LeftButton, pos=start)
    QTest.mouseMove(window, start + QPoint(-450, 0), 30)
    QTest.qWait(80)
    assert profile_value(controller).depths == (0, 0, 0, 0)
    QTest.mouseMove(window, start + QPoint(20, 0), 30)
    QTest.mouseRelease(window, Qt.LeftButton, pos=start + QPoint(20, 0))
    assert_depths(profile_value(controller).depths, (0.021, 0.042, 0.042, 0.021))
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert profile_value(controller) == before


def assert_depths(actual, expected):
    assert all(abs(a - b) < 1e-10 for a, b in zip(actual, expected, strict=True)), actual


def profile_preview(controller, window):
    before = profile_value(controller)
    reveal(window, "tissuePreviewStart")
    click(window, "tissuePreviewStart")
    settle(controller)
    type_value(window, "tissueProfileDepthValue", "0.06")
    settle(controller)
    assert profile_value(controller) == before
    assert_depths(
        controller.tissuePreview["settings"]["profile"]["depths"], (0.03, 0.06, 0.06, 0.03)
    )
    click(window, "tissuePreviewCancel")
    settle(controller)
    assert profile_value(controller) == before


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            run(inflation)
            run(stacking)
            run(profile)
            print("All four tissue authoring controls passed offscreen, including drag and undo.")
        finally:
            delete(app)
