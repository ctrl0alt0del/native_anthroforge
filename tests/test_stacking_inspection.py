"""Stacking explanations reuse accepted ordering and native material masks."""

from tests.test_tissue_stack_workflow import assembly


def inspect(session, target, other):
    session.command("tissue.inspect.stacking", target=target, other=other)
    session.wait()
    return session.command("tissue.inspect.status", kind="stacking")


def test_support_footprint_is_read_only_and_identifies_provider(session):
    _, provider, receiver = assembly(session)
    before, cursor = session.document, session.history.cursor
    value = inspect(session, receiver, provider)
    assert value["state"] == "ready", value
    report = value["report"]
    assert report["order"]["underlying"] == provider
    assert report["order"]["covering"] == receiver
    assert report["polygons"] and report["lines"] and len(report["lines"]) % 2 == 0
    assert session.document is before and session.history.cursor == cursor


def test_excluded_pair_has_no_effective_support_footprint(session):
    _, provider, receiver = assembly(session)
    session.command("tissue.stacking.relationship", target=receiver, other=provider, excluded=True)
    session.wait()
    value = inspect(session, receiver, provider)
    assert value["state"] == "ready", value
    assert not value["report"]["lines"] and not value["report"]["active"]


def test_changed_provider_marks_footprint_stale(session):
    _, provider, receiver = assembly(session)
    assert inspect(session, receiver, provider)["state"] == "ready"
    session.command("tissue.inflation", target=provider, changes=dict(amount=0.08))
    session.wait()
    assert session.command("tissue.inspect.status", kind="stacking")["state"] == "stale"


def test_pending_order_does_not_claim_new_settings_as_accepted_effect(session):
    _, provider, receiver = assembly(session)
    session.command("update_mode", entity=receiver, mode="MANUAL")
    session.command("tissue.stacking.configure", target=receiver, changes=dict(search=0.04))
    session.wait()
    value = inspect(session, receiver, provider)
    assert value["state"] == "failed" and "not current" in value["error"]
