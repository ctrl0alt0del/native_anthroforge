"""Command lifecycle contracts independent of individual domain implementations."""

from types import SimpleNamespace

import pytest

from anthroforge.application.command_contracts import catalogue, edit, method, query
from anthroforge.application.command_execution import execute
from anthroforge.application.commands import registered
from anthroforge.application.session import Session


@pytest.fixture
def session():
    value = Session()
    yield value
    value.close()


def test_catalogue_is_unique_immutable_and_shared():
    result = registered()
    assert result is registered()
    with pytest.raises(TypeError):
        result["made.up"] = result["inspect"]
    with pytest.raises(ValueError, match="Duplicate"):
        catalogue(((query("inspect", lambda _: None),) * 2,))
    for command in result.values():
        if command.kind == "edit":
            assert command.policy.mirror_guard and command.policy.variant_guard
            assert command.policy.transaction and command.policy.journal == "edit"


def test_dynamic_service_dispatch_uses_the_current_context():
    call = method("assembly.status")
    owner = SimpleNamespace(assembly=SimpleNamespace(status=lambda: "accepted"))
    assert call(owner) == "accepted"
    owner.assembly = SimpleNamespace(status=lambda: "variant")
    assert call(owner) == "variant"


def failing_edit(session):
    session.replace_document(name="temporary")
    raise ValueError("failed handler")


def test_implicit_failure_rolls_back_without_history(session):
    before, cursor = session.document, session.history.cursor
    with pytest.raises(ValueError, match="failed handler"):
        execute(session, edit("test.failure", failing_edit), {})
    assert session.document == before
    assert session.history.cursor == cursor
    assert session.history.before is None


def test_explicit_gesture_owns_failure_and_undo(session):
    session.begin()
    with pytest.raises(ValueError, match="failed handler"):
        execute(session, edit("test.failure", failing_edit), {})
    assert session.history.before is not None
    assert session.document.name == "temporary"
    session.cancel()
    assert session.document.name == "Untitled"


@pytest.mark.parametrize(
    "operation", ["assembly.import", "skeleton_update.apply", "painting.commit"]
)
def test_isolated_operations_reject_before_handler(session, operation):
    session.begin()
    with pytest.raises(ValueError, match="Finish the current gesture"):
        session.command(operation, token="not-a-candidate")
    assert session.history.before is not None
    session.cancel()


def test_profile_controls_are_declared_without_self_tracing():
    for name in ("profile.start", "profile.status", "profile.stop"):
        assert not registered()[name].profiled


def test_project_scope_is_declared_by_feature():
    assert registered()["skin.configure"].policy.project_scope
    assert registered()["skeleton_update.apply"].policy.project_scope
    assert registered()["attachments.enable"].policy.project_scope
    assert not registered()["scp.rename"].policy.project_scope
