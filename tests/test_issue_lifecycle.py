"""Failure isolation, dispatch freshness, history and repair lifecycle regressions."""

from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application.issues.providers import Provider
from anthroforge.application.issues.resolution import Solver
from anthroforge.core.issues import Issue
from tests.test_construction_contracts import create
from tests.test_issue_integration import records


def faulty(document, scope, cancel):
    if scope == "bad":
        raise RuntimeError("Diagnostic unavailable")
    return (Issue("isolation", scope, "GOOD", "Independent evidence"),)


def test_one_failed_scope_does_not_hide_other_checks(session):
    provider = Provider(
        "isolation", lambda _: {"bad", "good"}, lambda *_: set(), lambda *_: 1, faulty
    )
    session.issues.listening.register(provider)
    session.wait(5)
    assert len(records(session, provider="isolation")) == 1
    status = session.command("issues.status")
    assert not status["complete"] and not status["clean"]
    assert any(c["scope"] == "bad" and c["status"] == "FAILED" for c in status["checks"])


def broken_discovery(document):
    raise RuntimeError("Provider capture unavailable")


def test_discovery_failure_is_visible_and_other_providers_continue(session):
    provider = Provider("broken", broken_discovery, lambda *_: set(), lambda *_: 1, faulty)
    session.issues.listening.register(provider)
    session.wait(5)
    status = session.command("issues.status")
    assert any(c["provider"] == "broken" and c["error"] for c in status["checks"])
    assert not status["complete"]
    session.issues.listening.unregister("broken")
    assert session.command("issues.status")["complete"]


def test_query_marks_edits_stale_before_next_desktop_tick(session):
    entity = create(session)
    session.command("update_mode", mode="MANUAL")
    session.command("primitive.update", entity=entity, samples=40)
    session.wait(5)
    row = records(session, code="OUTPUT_PENDING")[0]
    session.command("primitive.update", entity=entity, samples=41)
    assert session.command("issues.get", identity=row["id"])["freshness"] == "stale"
    with pytest.raises(ValueError, match="stale"):
        session.command("issues.fix", identity=row["id"], name="evaluate")


def test_reporting_revision_replaces_previous_direct_evidence(session):
    first = Issue("direct", "scope", "PROBLEM", "Old", source="one")
    session.issues.reporting.report(first)
    session.issues.reporting.report(replace(first, source="two", summary="New"))
    rows = records(session, provider="direct")
    assert len(rows) == 1 and rows[0]["summary"] == "New"


def test_undo_discards_previous_epoch_findings_and_redo_checks_again(session):
    entity = create(session)
    session.command("update_mode", mode="MANUAL")
    session.command("primitive.update", entity=entity, samples=40)
    session.wait(5)
    row = records(session, code="OUTPUT_PENDING")[0]
    session.command("issues.dismiss", identity=row["id"])
    session.command("undo")
    session.wait(5)
    assert not records(session, code="OUTPUT_PENDING")
    session.command("redo")
    session.wait(5)
    assert records(session, code="OUTPUT_PENDING")


def test_successful_action_with_unresolved_finding_is_not_reported_done(session):
    entity = create(session)
    session.command("update_mode", mode="MANUAL")
    session.command("primitive.update", entity=entity, samples=40)
    session.wait(5)
    row = records(session, code="OUTPUT_PENDING")[0]
    solver = Solver("noop", "No operation", ("OUTPUT_PENDING",), lambda _: True, lambda _: ())
    session.issues.resolution.register(solver)
    session.command("issues.fix", identity=row["id"], name="noop")
    session.wait(5)
    assert session.command("issues.repairs")[-1]["state"] == "UNRESOLVED"


def test_cancel_queued_checks_finishes_coverage_without_clearing_evidence(session):
    session.issues.listening.synchronize()
    session.command("issues.cancel")
    status = session.command("issues.status")
    assert not status["complete"]
    assert any(c["status"] == "CANCELLED" for c in status["checks"])
    session.command("issues.recheck")
    session.wait(5)
    assert session.command("issues.status")["complete"]


def test_old_check_cleanup_cannot_fail_replacement_after_reset(session):
    from tests.test_issue_integration import slow_provider

    entered, release = Event(), Event()
    session.issues.listening.register(slow_provider(entered, release))
    session.scheduler.tick()
    session.scheduler.tick()
    session.issues.reset()
    release.set()
    session.wait(5)
    rows = records(session, provider="slow")
    assert rows and all(r["freshness"] == "current" for r in rows)
