"""Offscreen numeric gestures and actual direct creation controls; no desktop input."""

import json
import os
from dataclasses import replace
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from direct_workflow_acceptance import click, mouse_click, visible
from numeric_input_acceptance import find, reveal
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtTest import QTest
from tissue_editor_acceptance import (
    QQuickStyle,
    delete,
    native_runtime,
    profiler_application,
    run,
    settle,
)

from tests.test_attached_creation import surface_scene

OUTPUT = Path("build/direct-tissue-stable-inspectors")


def bounds(item):
    point = item.mapToScene(QPointF())
    return [point.x(), point.y(), item.width(), item.height()]


def feedback(controller, target, failure):
    document = controller.session.document
    item = document.entity(target)
    result = replace(item.result, error=failure, status="failed" if failure else "pending")
    changed = replace(item, result=result)
    controller.session.replace_document(
        entities=tuple(changed if e.id == target else e for e in document.entities)
    )
    controller.message = failure or "Calculation pending"
    controller.refresh()
    QTest.qWait(50)


def scenario(controller, window):
    target = controller.run("primitive.create", dict(kind="BODY"))
    controller.select(target)
    settle(controller)
    controller.run("update_mode", dict(entity=target, mode="MANUAL"))
    reveal(window, "primitiveSamplesValue")
    field = find(window, "primitiveSamplesValue")
    original = controller.session.document.entity(target).primitive.samples
    verify_scrub(controller, window, field, target, original)


def verify_scrub(controller, window, field, target, original):
    cursor = controller.session.history.cursor
    measured = scrub(controller, window, field, target)
    assert controller.session.history.cursor == cursor + 1
    controller.run("undo", {})
    assert controller.session.document.entity(target).primitive.samples == original
    assert not controller.session.history.before
    (OUTPUT / "layout.json").write_text(json.dumps(measured, indent=2), encoding="utf-8")


def scrub(controller, window, field, target):
    start = field.mapToScene(QPointF(field.width() / 2, field.height() / 2)).toPoint()
    expected = bounds(field)
    QTest.mousePress(window, Qt.LeftButton, pos=start)
    captured = []
    for offset, message in [(20, ""), (35, "A long calculation diagnostic. " * 40), (50, "")]:
        QTest.mouseMove(window, start + QPoint(offset, 0), 30)
        feedback(controller, target, message)
        assert field.property("scrubbing") and field.hasActiveFocus()
        assert bounds(field) == expected, (expected, bounds(field))
        captured.append(dict(offset=offset, bounds=bounds(field), value=field.property("value")))
    assert window.grabWindow().save(str(OUTPUT / "dragging-pending.png"))
    QTest.mouseRelease(window, Qt.LeftButton, pos=start + QPoint(50, 0))
    return captured


def membrane_action(controller, window):
    _, surface, _ = surface_scene(controller.session)
    controller.refresh()
    controller.select(surface.id)
    settle(controller)
    cursor = controller.session.history.cursor
    click(visible(window, "surfaceCreateMembrane"))
    settle(controller)
    assert controller.selectedData["kind"] == "MEMBRANE"
    assert controller.session.history.cursor == cursor + 1 and not window.property("modalOpen")
    mouse_click(window, "createTissueToolbar")
    settle(controller)
    assert controller.selectedData["is_tissue"]
    assert window.grabWindow().save(str(OUTPUT / "direct-tissue.png"))


def generic_surface_action(controller, window):
    _, surface, _ = surface_scene(controller.session)
    controller.refresh()
    controller.select(surface.id)
    settle(controller)
    cursor = controller.session.history.cursor
    mouse_click(window, "createTissueToolbar")
    settle(controller)
    tissue = controller.session.document.object(controller.selection)
    membrane = controller.session.document.object(tissue.source)
    assert controller.selectedData["is_tissue"] and membrane.id != surface.id
    assert all(controller.objectRecord(u.curve)["kind"] == "FIBER" for u in membrane.curves)
    assert controller.session.history.cursor == cursor + 1 and not window.property("modalOpen")


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        app.setFont(QFont("Segoe UI"))
        try:
            for check in (scenario, membrane_action, generic_surface_action):
                run(check)
            print("Stable numeric layout, focus, undo and direct construction actions passed.")
        finally:
            delete(app)


if __name__ == "__main__":
    main()
