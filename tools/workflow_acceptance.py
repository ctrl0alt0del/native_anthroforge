"""Real desktop interactions and GPU inspection export for the five workflow improvements."""

import json
import zipfile
from pathlib import Path

from activity_acceptance import wait_for
from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/workflow-017").resolve()


def settle(controller):
    wait_for(controller, lambda: not controller.session.scheduler.active_jobs)
    QTest.qWait(150)


def fixture(controller):
    session = controller.session
    root = session.command(
        "import", path=str(Path("examples/primitives/cube.obj").resolve()), units=1
    )["entity_id"]
    settle(controller)
    entity = session.command(
        "primitive.create", kind="BODY", parent=root, name="Editable curve body"
    )
    settle(controller)
    hook = session.command("control.create", entity=entity, name="Shared hook")
    settle(controller)
    controller.select(entity)
    controller.frameSelection()
    return root, entity, hook


def workspace_ui(controller, window, entity, hook):
    click(window, "manageWorkspace")
    units = find(window, "displayUnits")
    units.setProperty("currentIndex", 2)
    QMetaObject.invokeMethod(units, "activated", Qt.ConnectionType.DirectConnection, Q_ARG_INT(2))
    assert controller.session.workspace.display_units == "mm"
    controller.run("workspace.create", dict(name="Curve work", members=[entity, hook]))
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / "workspace.png"))
    QMetaObject.invokeMethod(find(window, "workspaceManager"), "close")


def Q_ARG_INT(value):
    from PySide6.QtCore import Q_ARG

    return Q_ARG(int, value)


def units_ui(controller, window, entity):
    controller.select(entity)
    field = click(window, "transform0")
    field.setProperty("text", "250")
    QTest.keyClick(window, Qt.Key.Key_Return)
    settle(controller)
    assert abs(controller.session.document.entity(entity).matrix[3] - 0.25) < 1e-8


def filters(controller, window, entity):
    controller.authoring.setEditing(True)
    editor = controller.authoring
    controller.run(
        "workspace.update", dict(hidden_categories=["handles"], unpickable_categories=["points"])
    )
    assert not editor.visualLayers["handles"] and editor.visualLayers["points"]
    assert editor._point_index.pick([0, 0, 10], [0, 0, -1], 100, 0) == -1
    geometry_filter(controller, entity)


def geometry_filter(controller, entity):
    controller.run(
        "workspace.update", dict(hidden_categories=["geometry"], unpickable_categories=[])
    )
    settle(controller)
    assert controller.authoring.visible and controller.authoring.visualLayers["curves"]
    assert entity not in controller.pick_ids
    controller.run("workspace.preset", dict(name="all"))
    settle(controller)
    assert entity in controller.pick_ids


def inspect_ui(controller, window):
    inspector = find(window, "inspector")
    panel = find(window, "dependencyInspector")
    panel.setProperty("expanded", True)
    QTest.qWait(80)
    flickable = inspector.property("contentItem")
    flickable.setProperty("contentY", panel.y())
    QTest.qWait(150)
    assert controller.inspection_panel.detail.get("geometry")["available"]
    assert window.grabWindow().save(str(OUTPUT / "editor.png"))


def export_report(controller, window, entity):
    path = OUTPUT / "desktop.afinspection.zip"
    controller.inspection_export.start(str(path))
    frozen = controller.session.document.revision
    controller.run("scp.rename", dict(entity=entity, name="Changed during export"))
    settle(controller)
    with zipfile.ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
        (OUTPUT / "inspection.png").write_bytes(archive.read("image.png"))
    assert data["revision"] == frozen and data["image"]["revision"] == frozen
    assert data["view"]["selected"] == entity
    assert next(r for r in data["entities"] if r["id"] == entity)["name"] == "Editable curve body"


def run(app):
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    window = engine.rootObjects()[0]
    try:
        root, entity, hook = fixture(controller)
        workspace_ui(controller, window, entity, hook)
        units_ui(controller, window, entity)
        filters(controller, window, entity)
        inspect_ui(controller, window)
        export_report(controller, window, entity)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        run(app)
    print(json.dumps(dict(workflow_acceptance=True, output=str(OUTPUT))))
