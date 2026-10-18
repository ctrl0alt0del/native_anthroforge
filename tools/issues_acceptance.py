"""Actual Issues delegates, evidence, navigation, dismissal and explicit repair."""

from pathlib import Path

from activity_acceptance import wait_for
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import click, find

from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.controller_actions import new_document
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/issues-016/gui").resolve()


def settle(controller):
    wait_for(
        controller,
        lambda: (
            not controller.session.scheduler.blocked
            and controller.session.issues.presentation.status()["complete"]
        ),
    )
    QTest.qWait(100)


def filter_rows(window, text):
    find(window, "issueSearch").setProperty("text", text)
    QTest.qWait(40)


def create_cycle(controller):
    session = controller.session
    entity = session.command("primitive.create", kind="BODY", name="Clavicle test")
    settle(controller)
    control = session.command("control.create", entity=entity, name="Shared hook")
    session.command("deformer.add", control=control, target={"owner": entity})
    settle(controller)
    session.command("control.attach", control=control, support=entity)
    settle(controller)
    controller.select(entity)
    controller.frameSelection()
    return entity, control


def select_first(controller, window):
    row = controller.issue_panel.model.rows[0]
    click(window, "issueRow-" + row["issueId"])
    assert controller.issue_panel.detail["id"] == row["issueId"]
    return row["issueId"]


def inspect_cycle(controller, window):
    entity, control = create_cycle(controller)
    click(window, "issuesToggle")
    filter_rows(window, "DEPENDENCY_BLOCKED")
    identity = select_first(controller, window)
    click(window, "issueSelectTarget")
    assert controller.selection == controller.issue_panel.detail["target"]
    click(window, "issueFrameTarget")
    QTest.qWait(150)
    assert window.grabWindow().save(str(OUTPUT / "dependency-issues.png"))
    dismissal(controller, window, identity)
    controller.session.command("control.follow", control=control, entity=entity)
    settle(controller)
    assert not controller.issue_panel.model.rows
    return entity


def dismissal(controller, window, identity):
    count = controller.issue_panel.model.rowCount()
    click(window, "issueDismiss")
    assert controller.issue_panel.model.rowCount() == count - 1
    click(window, "issueShowDismissed")
    assert controller.issue_panel.model.rowCount() == count
    click(window, "issueRow-" + identity)
    click(window, "issueDismiss")
    assert identity not in controller.session.issues.repository.dismissed
    click(window, "issueShowDismissed")


def repair_pending(controller, window, entity):
    controller.session.command("update_mode", mode="MANUAL")
    controller.session.command("primitive.update", entity=entity, samples=40)
    settle(controller)
    filter_rows(window, "OUTPUT_PENDING")
    select_first(controller, window)
    assert window.grabWindow().save(str(OUTPUT / "manual-pending.png"))
    click(window, "issueFix-evaluate")
    settle(controller)
    assert controller.session.command("issues.repairs")[-1]["state"] == "DONE"
    assert not controller.issue_panel.model.rows


def model_and_new(controller, window):
    filter_rows(window, "")
    model = controller.issue_panel.model
    index = QPersistentModelIndex(model.index(0))
    new_document(controller)
    settle(controller)
    assert controller.issue_panel.model is model and not index.isValid()
    assert model.rowCount() == 0 and controller.issue_panel.state["complete"]
    assert window.grabWindow().save(str(OUTPUT / "new-document.png"))


def run():
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        entity = inspect_cycle(controller, window)
        repair_pending(controller, window, entity)
        model_and_new(controller, window)
        assert not warnings, warnings
        print("Issues navigation/filter/dismiss/restore/repair/verification/New passed", flush=True)
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run()
        finally:
            delete(app)
