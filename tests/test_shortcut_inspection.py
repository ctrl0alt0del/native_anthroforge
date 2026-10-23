"""Shortcut inspection cannot alter anatomy, history or evaluation intent."""

import json

import pytest

from tests.test_driving_formulas import curve, driver, reference


def test_effects_explain_actual_graph_without_writing(session):
    target = curve(session)
    key, formula = driver(session, target, "round(value)", value=8)
    session.wait(5)
    before, cursor = session.document, session.history.cursor
    effects = session.command("shortcut.effects", shortcut=key)
    assert any(r["owner"] == target and r["direct"] for r in effects["rows"])
    assert any(r["owner"] == formula for r in effects["rows"])
    assert session.command("shortcut.progress", shortcut=key)["state"] == "complete"
    json.dumps(effects)
    assert session.document is before and session.history.cursor == cursor


def test_formula_evidence_distinguishes_captured_and_current_values(session):
    target = curve(session)
    key, _ = driver(session, target, "round(value)", value=8)
    session.wait(5)
    row = session.command("shortcut.formulas", shortcut=key)["rows"][0]
    assert row["inputs"][0]["captured_value"] == 8
    assert row["result"]["value"] == 8
    session.shortcut_observation.formulas.clear()
    row = session.command("shortcut.formulas", shortcut=key)["rows"][0]
    assert row["inputs"][0]["value"] == 8
    assert not row["inputs"][0]["captured_available"]


def test_edit_observation_tracks_publication_and_undo(session):
    target = curve(session)
    key, _ = driver(session, target, "round(value)", value=8)
    session.wait(5)
    session.command("driver.value", driver=key, value=12)
    session.wait(5)
    value = session.command("shortcut.progress", shortcut=key)
    assert value["edit"] and value["updated_outputs"] > 0
    assert value["state"] == "complete"
    session.command("undo")
    assert session.command("shortcut.progress", shortcut=key)["state"] == "superseded"


def test_cycle_explanation_separates_participant_and_blocked(session):
    a, b, c = (curve(session, name) for name in ("A", "B", "C"))
    ka, _ = driver(session, a, "x", inputs=[dict(name="x", property=reference(b))])
    driver(session, b, "x", inputs=[dict(name="x", property=reference(a))])
    kc, _ = driver(session, c, "x", inputs=[dict(name="x", property=reference(b))])
    session.wait(5)
    assert session.command("shortcut.formulas", shortcut=ka)["rows"][0]["participant"]
    downstream = session.command("shortcut.formulas", shortcut=kc)["rows"][0]
    assert downstream["blocked"] and not downstream["participant"]
    assert session.command("shortcut.progress", shortcut=ka)["state"] == "failed"


def test_attachment_inspection_does_not_capture_or_rebind(session, assembly):
    _, child = assembly
    ref = reference(child, ("transform", "scale"), 0)
    key = session.command("shortcut.expose", reference=ref)
    before = session.document
    row = session.command("shortcut.attachment_policy", shortcut=key)
    assert row["scope"] == child and not row["captured"]
    assert row["rows"][0]["binding_available"]
    assert session.document is before


def test_effects_validate_pages_and_deleted_identity(session):
    target = curve(session)
    key = session.command("shortcut.expose", reference=reference(target))
    with pytest.raises(ValueError, match="limit"):
        session.command("shortcut.effects", shortcut=key, limit=1000)
    with pytest.raises(ValueError, match="Unknown shortcut"):
        session.command("shortcut.effects", shortcut="missing")
    row = session.command("shortcut.effects", shortcut=key, limit=1)
    assert len(row["rows"]) == 1 and row["total"] > 1
