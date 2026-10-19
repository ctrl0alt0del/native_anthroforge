"""Large optional selections retain identities, mandatory rows and filtered bulk scope."""

import pytest
from PySide6.QtCore import QCoreApplication, QPersistentModelIndex
from PySide6.QtTest import QAbstractItemModelTester, QSignalSpy

from anthroforge.desktop.choice_model import ChoiceModel


@pytest.fixture
def choices():
    app = QCoreApplication.instance() or QCoreApplication([])
    model = ChoiceModel()
    tester = QAbstractItemModelTester(model, QAbstractItemModelTester.FailureReportingMode.Fatal)
    model.synchronize([record(i) for i in range(120)])
    yield model
    assert app and tester


def record(index):
    return dict(
        key=str(index),
        label=f"Point {index + 1}",
        detail="Authored point",
        chosen=True,
        locked=index in (0, 119),
        reason="Endpoint" if index in (0, 119) else "",
    )


def test_filtered_bulk_changes_only_shown_unlocked_rows(choices):
    choices.filter("point 1", 0)
    assert choices.counts["shown"] == 32
    choices.chooseShown(False)
    assert choices.records.rows[0]["chosen"] and choices.records.rows[119]["chosen"]
    assert choices.records.rows[1]["chosen"] and not choices.records.rows[10]["chosen"]
    choices.filter("", 2)
    assert choices.rowCount() == 30
    choices.chooseShown(True)
    assert choices.rowCount() == 0 and len(choices.selected) == 120


def test_membership_updates_do_not_reset_model_or_renumber_filtered_points(choices):
    resets = QSignalSpy(choices.modelReset)
    persistent = QPersistentModelIndex(choices.records.index(110))
    choices.choose("110", False)
    choices.filter("111", 0)
    role = next(key for key, value in choices.roleNames().items() if value == b"label")
    assert choices.index(0, 0).data(role) == "Point 111"
    choices.synchronize([record(i) for i in range(120)])
    assert persistent.isValid() and persistent.row() == 110
    assert resets.count() == 0 and choices.rowCount() == 1
