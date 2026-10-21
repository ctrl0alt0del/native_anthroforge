"""Inspection owns read-only work and never turns stale evidence into accepted anatomy."""

from dataclasses import replace
from weakref import ref

from anthroforge.application import tissue_inspection as inspection
from anthroforge.application.issues.tissue_geometry import NAME
from tests.test_tissue_workflow import assembly


def test_pending_authored_settings_keep_accepted_inspection_current(session):
    _, _, key = assembly(session)
    session.command("tissue.inspect.compare", target=key, stage="rest", reference="base")
    session.wait()
    item = session.document.object(key)
    pending = replace(item.rest_result, pending=(key,), status="pending", error="")
    document = session.document
    changed = replace(item, rest_result=pending)
    session.document = replace(
        document, objects=tuple(changed if o.id == key else o for o in document.objects)
    )
    assert inspection.status(session, "comparison")["state"] == "ready"
    session.document = document


def test_cancel_releases_comparison_without_document_or_undo_edits(session):
    _, _, key = assembly(session)
    before, cursor = session.document, session.history.cursor
    session.command("tissue.inspect.compare", target=key, stage="rest", reference="base")
    session.wait()
    resource = ref(session.tissue_inspection.values["comparison"].asset["resource"])
    session.command("tissue.inspect.cancel")
    session.scheduler.tick()
    assert inspection.status(session, "comparison")["state"] == "idle"
    assert resource() is None
    assert session.document is before and session.history.cursor == cursor


def test_failed_query_retains_tissue_and_can_be_retried(session):
    _, _, key = assembly(session)
    before = session.document.object(key).result
    session.command(
        "tissue.inspect.point", target=key, stage="final", triangle=-1, weights=[1, 0, 0]
    )
    session.wait()
    assert inspection.status(session, "point")["state"] == "failed"
    assert session.document.object(key).result == before
    session.command(
        "tissue.inspect.point", target=key, stage="final", triangle=0, weights=[1, 0, 0]
    )
    session.wait()
    assert inspection.status(session, "point")["state"] == "ready"


def test_read_validation_rejects_new_geometry_and_keeps_old_output(session):
    _, _, key = assembly(session)
    before = session.document.object(key).rest_result.asset
    session.command("tissue.inflation", target=key, changes=dict(amount=0.09))
    session.wait()
    query = dict(target=key, stage="rest", triangle=0, weights=[1, 0, 0], expected_asset=before)
    session.command("tissue.inspect.point", **query)
    session.wait()
    status = inspection.status(session, "point")
    assert status["state"] == "failed" and "changed" in status["error"]


def test_explicit_checks_stay_stale_after_undo_until_requested(session):
    _, _, key = assembly(session)
    session.command("tissue.inspect.check", target=key)
    session.wait()
    session.command("tissue.inflation", target=key, changes=dict(amount=0.09))
    session.wait()
    session.command("undo")
    session.wait()
    assert NAME not in session.issues.listening.running
    session.command("tissue.inspect.check", target=key)
    session.wait()
    assert session.issues.repository.states[NAME, key + ":final"].status == "COMPLETE"
