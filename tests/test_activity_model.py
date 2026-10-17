import pytest
from PySide6.QtCore import QCoreApplication, QModelIndex, QPersistentModelIndex
from PySide6.QtTest import QAbstractItemModelTester, QSignalSpy

from anthroforge.core.jobs import Job
from anthroforge.desktop.activity_model import HISTORY_LIMIT, ROLES, ActivityModel


@pytest.fixture
def model():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = ActivityModel(clock=lambda: 20.0)
    tester = QAbstractItemModelTester(value, QAbstractItemModelTester.FailureReportingMode.Fatal)
    yield value
    assert app and tester


def job(name="Work", **changes):
    value = Job(
        name, frozenset(("bone",)), lambda doc: doc, lambda doc, cancel: None, lambda _: None
    )
    value.created = 10.0
    for key, data in changes.items():
        setattr(value, key, data)
    return value


def role(name):
    return next(key for key, value in ROLES.items() if value == name)


def test_inserting_and_reordering_keeps_job_identity_without_reset(model):
    a, b, c = job("a"), job("b"), job("c")
    resets = QSignalSpy(model.modelReset)
    model.synchronize([a, b], {})
    persistent = QPersistentModelIndex(model.index(1))
    model.synchronize([a, b, c], {})
    assert persistent.row() == 2 and persistent.data(role("jobId")) == a.id
    model.synchronize([c, a, b], {})
    assert persistent.row() == 1 and persistent.data(role("jobId")) == a.id
    assert [r["jobId"] for r in model.rows] == [b.id, a.id, c.id]
    assert resets.count() == 0


def test_elapsed_only_changes_elapsed_role_without_status_or_structure(model):
    item = job()
    model.synchronize([item], {"bone": "Bone"})
    changed, summary = QSignalSpy(model.dataChanged), QSignalSpy(model.summaryChanged)
    inserted, removed = QSignalSpy(model.rowsInserted), QSignalSpy(model.rowsRemoved)
    model.clock = lambda: 21.004
    model.synchronize([item], {"bone": "Bone"})
    model.synchronize([item], {"bone": "Bone"})
    assert changed.count() == 1 and changed.at(0)[2] == [role("elapsed")]
    assert model.rows[0]["elapsed"] == 11.0
    assert summary.count() == inserted.count() == removed.count() == 0


def test_failure_cancel_retry_and_finished_elapsed_are_presented(model):
    item = job(state="cancelling", retry=lambda: None)
    model.synchronize([item], {})
    assert model.activeCount == 1 and model.rows[0]["cancellable"]
    item.state, item.error, item.finished = "failed", "Invalid input", 18.5
    model.synchronize([item], {})
    assert model.activeCount == 0 and model.hasFailures
    assert model.rows[0]["retryable"] and not model.rows[0]["cancellable"]
    assert model.rows[0]["error"] == "Invalid input"
    changed = QSignalSpy(model.dataChanged)
    model.clock = lambda: 100.0
    model.synchronize([item], {})
    assert model.rows[0]["elapsed"] == 8.5 and changed.count() == 0


def test_target_rename_updates_only_target_role(model):
    item = job(outputs=frozenset(("bone", "missing")))
    model.synchronize([item], {"bone": "Old"})
    changed = QSignalSpy(model.dataChanged)
    model.synchronize([item], {"bone": "Renamed"})
    assert model.rows[0]["targets"] == "Renamed, Project"
    assert changed.at(0)[2] == [role("targets")]


def test_history_retention_and_document_clear_use_row_notifications(model):
    jobs = [job(str(index)) for index in range(HISTORY_LIMIT + 3)]
    model.synchronize(jobs[:HISTORY_LIMIT], {})
    old = QPersistentModelIndex(model.index(HISTORY_LIMIT - 1))
    resets = QSignalSpy(model.modelReset)
    model.synchronize(jobs, {})
    assert model.rowCount() == HISTORY_LIMIT and not old.isValid()
    assert model.rows[-1]["jobId"] == jobs[3].id
    model.synchronize([], {})
    assert model.rowCount() == model.activeCount == 0 and not model.hasFailures
    assert resets.count() == 0
    assert model.data(QModelIndex()) is None


def test_projection_does_not_mutate_job_or_serialize_workload(model):
    item = job()
    before = dict(vars(item))
    item.describe = lambda: pytest.fail("Activity must not serialize full job descriptions")
    model.synchronize([item], {})
    assert all(getattr(item, key) == value for key, value in before.items())
