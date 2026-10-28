"""Captured operations use the same coordinator while leaving live document ownership intact."""

from anthroforge.application import isolated_execution
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE


def test_isolated_session_has_independent_publication_and_owned_execution(session):
    before = session.document
    cancel = NativeCancellation(session.engine)
    isolated = isolated_execution.create(
        before, session.resources, session.preferences.value, cancel
    )
    try:
        key = isolated.command("import", path=str(CUBE), units=1)["entity_id"]
        isolated_execution.settle(isolated, cancel)
        assert isolated.document.entity(key).result.asset in isolated.assets
        assert session.document is before and not session.assets
        assert isinstance(isolated.scheduler.pool, isolated_execution.WorkerExecutor)
    finally:
        isolated.close()
    assert not cancel.is_set()


def test_child_cancellation_preserves_parent_and_observes_outer_cancel(session):
    parent = NativeCancellation(session.engine)
    child = isolated_execution.ChildCancellation(parent)
    child.set()
    assert child.is_set() and not parent.is_set()
    sibling = isolated_execution.ChildCancellation(parent)
    assert sibling.handle == parent.handle and not sibling.is_set()
    parent.set()
    assert sibling.is_set()
