"""Exercise long-curve presentation in a large document with the inspector visible/hidden."""

import json
from dataclasses import replace
from pathlib import Path

from primitive_acceptance import settle
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from standalone_audit import document_fixture
from ui_acceptance import find

from anthroforge.application.history import History
from anthroforge.core.construction import CurvePoint
from anthroforge.core.entities import Attachment
from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/standalone-optimizations/projection").resolve()


def setup(controller):
    document = document_fixture(512)
    body = document.entity("body")
    points = tuple(CurvePoint(position=(i / 127 - 0.5, 0, 0)) for i in range(128))
    curve = replace(body.primitive.curves[0], points=points, resolution=4)
    body = long_body(body, curve)
    document = replace(document, entities=(*document.entities[:-1], body))
    session = controller.session
    session.document, session.history = document, History(document)
    session.command("evaluate", entities=[body.id])
    session.wait(timeout=10)
    controller.refresh()
    controller.select(body.id)
    controller.authoring.setEditing(True)
    return curve


def long_body(body, curve):
    attachment = Attachment(parent_mode="OBJECT_ORIGIN", child_mode="OBJECT_ORIGIN")
    return replace(body, primitive=replace(body.primitive, curves=(curve,)), attachment=attachment)


def edit(controller, curve, height):
    controller.authoring.edit(
        "point.update",
        dict(entity="body", curve=curve.id, point=curve.points[64].id, position=[0, 0, height]),
    )
    settle(controller)
    assert (
        controller.session.document.entity("body").primitive.curves[0].points[64].position[2]
        == height
    )


def select_middle(controller, curve):
    row = next(
        r
        for r in controller.authoring.componentRows
        if r["point"] == curve.points[64].id and r["part"] == "position"
    )
    controller.authoring.selectComponent(row["key"], False)
    return tuple(controller.authoring.selection)


def exercise(controller, window, curve):
    controller.frameSelection()
    inspector = find(window, "inspector")
    selection = select_middle(controller, curve)
    for visible, height in ((True, 0.1), (False, 0.2)):
        inspector.setVisible(visible)
        edit(controller, curve, height)
        assert tuple(controller.authoring.selection) == selection and len(controller.rows) == 512
    inspector.setVisible(True)
    controller.run("undo", {})
    assert (
        controller.session.document.entity("body").primitive.curves[0].points[64].position[2] == 0.1
    )
    finish(controller, window)


def finish(controller, window):
    controller.run("evaluate", dict(entities=["body"]))
    settle(controller)
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / "long-curve.png"))
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    try:
        curve = setup(controller)
        exercise(controller, engine.rootObjects()[0], curve)
        assert not warnings, warnings
        report()
    finally:
        controller.close()
        delete(engine)


def report():
    result = dict(passed=True, entities=512, curve_points=128, inspector_visible_and_hidden=True)
    (OUTPUT / "acceptance.json").write_text(json.dumps(result))
    print(json.dumps(result))


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
