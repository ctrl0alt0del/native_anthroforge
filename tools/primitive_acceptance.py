"""Desktop construction acceptance using the production Qt/QML application."""

import json
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/primitive-review/gui").resolve()


def settle(controller):
    for _ in range(400):
        QTest.qWait(10)
        if not controller.session.scheduler.blocked and not controller.render_model.pending:
            QTest.qWait(100)
            return
    raise AssertionError("Editor did not finish calculation/publication.")


def screenshot(window, name):
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def source_curve(controller, entity, index=0):
    item = controller.session.document.entity(entity)
    return controller.session.document.object(item.primitive.curves[index].curve)


def create_loft(controller, window):
    controller.authoring.create("LOFT", "")
    settle(controller)
    entity = controller.selection
    curve = source_curve(controller, entity)
    controller.authoring.edit(
        "point.update",
        dict(entity=entity, curve=curve.id, point=curve.points[0].id, position=[-0.5, -0.15, 0.2]),
    )
    settle(controller)
    controller.viewport_view.frameSelection()
    QTest.qWait(150)
    screenshot(window, "loft-edit")
    assert len(controller.authoring.lines) > 100
    return entity


def edit_cage(controller, window):
    controller.authoring.addDeformer("LATTICE")
    settle(controller)
    cage = controller.selection
    controller.authoring.edit(
        "lattice.point", dict(control=cage, index=7, position=[0.5, 0.5, 1.2])
    )
    settle(controller)
    screenshot(window, "lattice-edit")
    assert controller.selection_view.selectedData["kind"] == "LATTICE"
    assert len(controller.authoring.lines) == 24
    return cage


def edit_hook(controller, window):
    key = controller.authoring.componentRows[7]["key"]
    controller.authoring.selectComponent(key, False)
    controller.authoring.addDeformer("HOOK")
    settle(controller)
    assert controller.selection_view.selectedData["kind"] == "HOOK"
    controller.viewport_view.beginTransform("Move")
    controller.viewport_view.dragTransform(2, 0.1)
    controller.viewport_view.endTransform(False)
    settle(controller)
    screenshot(window, "hook-edit")


def roundtrip(controller, entity):
    path = str(OUTPUT / "primitive-workflow.anthroforge")
    controller.run("save", dict(path=path, blocked_policy="wait"))
    settle(controller)
    controller.run("open", dict(path=path))
    settle(controller)
    controller.selection_view.select(entity)
    assert len(controller.session.document.controls) == 2


def verify(controller, window):
    window.resize(1500, 950)
    entity = create_loft(controller, window)
    cage = edit_cage(controller, window)
    edit_hook(controller, window)
    controller.selection_view.select(cage)
    settle(controller)
    roundtrip(controller, entity)
    screenshot(window, "reopened")
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    return controller.session.scheduler.metrics.report()


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, None)
    try:
        result = verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        report = dict(primitive_acceptance=True, warnings=warnings, metrics=result)
        name = report_name()
        (OUTPUT / name).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report))
    finally:
        controller.close()


def report_name():
    return next(
        (
            mode + ".json"
            for mode in ("interaction", "performance", "workshop")
            if "--" + mode in sys.argv
        ),
        "acceptance.json",
    )


if __name__ == "__main__":
    if "--interaction" in sys.argv:
        from primitive_interaction import verify
    if "--performance" in sys.argv:
        from primitive_performance import verify
    if "--workshop" in sys.argv:
        from primitive_workshop import verify

    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
