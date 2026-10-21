"""Accepted-stage provenance, advisory checks and read-only lifecycle contracts."""

import pytest

from anthroforge.application.issues.tissue_geometry import NAME
from tests.test_tissue_workflow import assembly


def test_stage_comparison_retains_anatomy_and_reports_material_displacement(session):
    _, _, key = assembly(session)
    before, history = session.document, len(session.history.entries)
    session.command("tissue.inspect.compare", target=key, stage="rest", reference="base")
    session.wait()
    value = session.command("tissue.inspect.status", kind="comparison")
    assert value["state"] == "ready", value
    assert value["report"]["maximum"] > 0
    assert session.document is before and len(session.history.entries) == history
    session.command("tissue.inspect.compare", target=key, stage="final", reference="intrinsic")
    session.wait()
    assert session.command("tissue.inspect.status", kind="comparison")["report"]["maximum"] == 0


def test_changed_stages_make_inspection_stale_without_recomputing(session):
    _, _, key = assembly(session)
    session.command("tissue.inspect.compare", target=key, stage="rest", reference="base")
    session.wait()
    session.command("tissue.inflation", target=key, changes=dict(amount=0.07))
    session.wait()
    assert session.command("tissue.inspect.status", kind="comparison")["state"] == "stale"


def test_geometry_checks_are_manual_and_advisory(session):
    _, _, key = assembly(session)
    assert not any(p == NAME for p, _ in session.issues.repository.states)
    before = session.document
    session.command("tissue.inspect.check", target=key)
    session.wait()
    state = session.issues.repository.states[NAME, key + ":final"]
    assert state.status == "COMPLETE", state
    assert session.document is before
    session.command("tissue.inflation", target=key, changes=dict(amount=0.08))
    session.wait()
    assert session.issues.repository.states[NAME, key + ":final"].status == "PENDING"
    assert NAME not in session.issues.listening.running


def test_point_explanation_uses_accepted_stage(session):
    _, _, key = assembly(session)
    session.command("tissue.inspect.point", target=key, stage="final", triangle=0, weights=[0.2, 0.3, 0.5])
    session.wait()
    value = session.command("tissue.inspect.status", kind="point")
    assert value["state"] == "ready", value
    assert value["report"]["point"]["base_available"]
    assert value["report"]["sources"]
    assert value["report"]["asset"] == session.document.object(key).final_result.asset


def test_invalid_stage_does_not_start_work(session):
    _, _, key = assembly(session)
    with pytest.raises(ValueError, match="Choose base"):
        session.command("tissue.inspect.compare", target=key, stage="invented")
