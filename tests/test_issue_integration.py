"""Advisory checks use the shared coordinator and never change authored state."""

from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application.issues.providers import Provider
from anthroforge.core.issues import Issue
from tests.test_construction_contracts import create, hook


def records(session, **filters):
    return session.command("issues.list", filters=filters, limit=200)["records"]


def test_clean_check_does_not_change_document_or_checkpoint(session):
    before = session.document
    session.wait(5)
    assert session.command("issues.status")["clean"]
    assert session.document is before and session.scheduler.checkpoint is before
    assert not session.scheduler.blocked and session.history.cursor == 0


def test_cycle_is_reported_then_cleared_without_losing_accepted_geometry(session):
    entity = create(session)
    control = hook(session, entity)
    asset = session.document.entity(entity).asset
    session.command("control.attach", control=control, support=entity)
    session.wait(5)
    assert records(session, code="DEPENDENCY_BLOCKED")
    assert session.document.entity(entity).asset == asset
    session.command("control.follow", control=control, entity=entity)
    session.wait(5)
    assert not records(session, code="DEPENDENCY_BLOCKED")


def test_manual_pending_has_explicit_verified_recalculate(session):
    entity = create(session)
    session.command("update_mode", mode="MANUAL")
    session.command("primitive.update", entity=entity, samples=40)
    session.wait(5)
    row = records(session, code="OUTPUT_PENDING")[0]
    session.command("issues.fix", identity=row["id"], name="evaluate")
    session.wait(5)
    session.scheduler.tick()
    assert not records(session, code="OUTPUT_PENDING")
    assert session.command("issues.repairs")[-1]["state"] == "DONE"


def test_readonly_workspace_and_edit_transaction_prohibit_repairs(session):
    entity = create(session)
    session.command("update_mode", mode="MANUAL")
    session.command("primitive.update", entity=entity, samples=40)
    session.wait(5)
    row = records(session, code="OUTPUT_PENDING")[0]
    session.begin()
    assert session.command("issues.fixes", identity=row["id"]) == []
    session.cancel()
    group = session.command("scp.wrap_root", name="Group")
    session.command("workspace.create", name="Other", members=[group])
    assert session.command("issues.fixes", identity=row["id"]) == []


def slow_provider(entered, release):
    def check(document, scope, cancel):
        entered.set()
        release.wait(2)
        return (Issue("slow", scope, "OLD", "Old evidence"),)

    return Provider("slow", lambda _: {"document"}, lambda *_: set(), lambda d, _: d.id, check)


@pytest.mark.parametrize("policy", ["pending", "wait", "checkpoint"])
def test_cancelled_readonly_check_cannot_publish_or_block_save(session, tmp_path, policy):
    session.wait(5)
    entered, release = Event(), Event()
    session.issues.listening.register(slow_provider(entered, release))
    session.scheduler.tick()
    assert entered.wait(2) and not session.scheduler.blocked
    session.command("save", path=str(tmp_path / "advisory.anthroforge"), blocked_policy=policy)
    assert session.issues.listening.running["slow"].active
    session.command("issues.cancel", provider="slow")
    release.set()
    session.wait(5)
    assert not records(session, provider="slow")
    assert not session.command("issues.status")["complete"]


def test_deleted_entity_and_open_remove_obsolete_scope(session, tmp_path):
    entity = create(session)
    path = str(tmp_path / "clean.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    fail_entity(session, entity)
    session.wait(5)
    assert records(session, code="EVALUATION_FAILED")
    session.command("open", path=path)
    session.wait(5)
    assert not records(session, code="EVALUATION_FAILED")
    session.command("scp.delete", entity=entity)
    session.wait(5)
    assert not records(session, target=entity)


def fail_entity(session, entity):
    value = session.document.entity(entity)
    session.replace_entities(
        {entity: replace(value, status="failed", error="Fixture")}, authored=False
    )
