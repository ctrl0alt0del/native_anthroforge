"""Exercise actual Activity delegates, controls and document replacement."""

from pathlib import Path

from primitive_acceptance import settle
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from snap_drag_diagnostic import fixture_entities
from ui_acceptance import click, find

from anthroforge.core.jobs import Job
from anthroforge.desktop.app import create_engine, open_controller
from anthroforge.desktop.controller_actions import new_document
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/activity-015/gui").resolve()


def failed_input(document, cancel):
    raise ValueError("Acceptance: invalid source geometry")


def queued_job(controller, execute):
    job = Job(
        "Activity acceptance",
        frozenset((controller.selection,)),
        lambda doc: doc,
        execute,
        lambda _: None,
    )
    controller.session.scheduler.submit(job)
    controller.notify()
    return job


def wait_for(controller, predicate):
    for _ in range(300):
        QTest.qWait(20)
        if predicate():
            return
    raise AssertionError("Activity lifecycle did not reach expected state")


def displayed_state(controller, item):
    return next(
        (r["jobState"] for r in controller.activity_model.rows if r["jobId"] == item.id), ""
    )


def cancel_and_retry(controller, window):
    retried = []
    item = queued_job(controller, lambda document, cancel: cancel.wait(5))
    item.retry = lambda: retried.append(queued_job(controller, lambda doc, cancel: None))
    wait_for(controller, lambda: displayed_state(controller, item) == "running")
    row = find(window, "activityJob-" + item.id)
    controller.notify()
    assert find(window, "activityJob-" + item.id) is row
    click(window, "cancelJob-" + item.id)
    wait_for(controller, lambda: displayed_state(controller, item) == "cancelled")
    click(window, "retryJob-" + item.id)
    wait_for(controller, lambda: bool(retried) and not controller.activity_model.activeCount)
    assert not controller.activity_model.activeCount


def failure_and_rename(controller, window):
    item = queued_job(controller, failed_input)
    wait_for(controller, lambda: displayed_state(controller, item) == "failed")
    assert controller.activity_model.hasFailures
    row = find(window, "activityJob-" + item.id)
    assert row.property("error") == "Acceptance: invalid source geometry"
    controller.run("scp.rename", dict(entity=controller.selection, name="Renamed target"))
    QTest.qWait(50)
    assert find(window, "activityJob-" + item.id) is row
    assert row.property("targets") == "Renamed target"
    assert window.grabWindow().save(str(OUTPUT / "failure.png"))


def document_switch(controller, window):
    model = controller.activity_model
    index = QPersistentModelIndex(model.index(0))
    new_document(controller)
    QTest.qWait(100)
    assert controller.activity_model is model
    jobs = controller.session.scheduler.registry.by_id
    assert all(jobs[row["jobId"]].kind == "issue_check" for row in model.rows)
    assert not index.isValid() and not model.hasFailures and not model.activeCount
    assert window.grabWindow().save(str(OUTPUT / "new-document.png"))


def exercise(controller, window):
    controller.select(fixture_entities(controller, 0.5))
    settle(controller)
    window.setProperty("activityOpen", True)
    QTest.qWait(250)
    cancel_and_retry(controller, window)
    failure_and_rename(controller, window)
    window.setProperty("activityOpen", False)
    hidden = queued_job(controller, lambda doc, cancel: None)
    wait_for(controller, lambda: hidden.state == "succeeded")
    document_switch(controller, window)


def run():
    controller, warnings = open_controller(None), []
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        print("Activity cancel/retry/failure/rename/hidden updates/New passed", flush=True)
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
