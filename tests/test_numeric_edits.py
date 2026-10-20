"""Numeric scrubbing uses existing history rather than producing per-motion undo."""

from PySide6.QtCore import QObject

from anthroforge.desktop.numeric_edits import NumericEdits


class Controller(QObject):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def run(self, operation, arguments):
        return self.session.command(operation, **arguments)


def change(session, target, x):
    session.command("scp.transform", entity=target, values=[x, 0, 0, 0, 0, 0, 1, 1, 1])


def test_scrub_commits_one_undo_action(session):
    target = session.command("scp.empty", name="Numeric test")
    service, owner = NumericEdits(Controller(session)), QObject()
    cursor = session.history.cursor
    assert service.begin(owner)
    for x in (0.01, 0.02, 0.03):
        change(session, target, x)
    service.commit(owner)
    assert session.history.cursor == cursor + 1 and not service.active
    session.command("undo")
    assert session.document.entity(target).matrix[3] == 0


def test_scrub_cancel_restores_values_and_rejects_nested_transactions(session):
    target = session.command("scp.empty", name="Numeric test")
    service, owner = NumericEdits(Controller(session)), QObject()
    before = session.document
    assert service.begin(owner)
    assert not service.begin(QObject())
    change(session, target, 0.5)
    service.cancel()
    assert session.document == before and session.history.before is None
    session.command("begin")
    assert not service.begin(owner)
    session.command("cancel")


def test_only_current_scrub_owner_can_cancel_when_destroyed(session):
    from shiboken6 import delete

    session.command("scp.empty", name="Numeric test")
    service, first, second = NumericEdits(Controller(session)), QObject(), QObject()
    assert service.begin(first)
    service.commit(first)
    assert service.begin(second)
    delete(first)
    assert service.active
    delete(second)
    assert not service.active and session.history.before is None
