"""Displayed source values match evaluation without overwriting authored overrides."""

from dataclasses import replace

from anthroforge.application import skin_capture, skin_fit_results, skin_operations
from anthroforge.core.skin import EnvelopeSettings, SkinContributor
from anthroforge.desktop import skin_contributor
from tests.test_skin_fit_jobs import fit, setup


def test_inherited_values_and_auto_collagen_match_capture(session, assembly):
    target, _ = assembly
    item = session.document.entity(target)
    session.replace_entities({target: replace(item, name="Ear cartilage")})
    session.command("skin.configure", section="envelope_settings", values=dict(gap_strength=0.25))
    state = skin_contributor.describe(session, target)
    assert state["effective"]["gap_strength"] == 0.25
    assert state["effective"]["collagen"] == 0
    assert state["settings"]["gap_strength"] == 1 and state["settings"]["collagen"] == 1
    source = type("Source", (), dict(identity=type("Identity", (), dict(owner=target, kind="SCP"))))
    assert skin_capture.policy(session.document, source)[1] == 0.25


def test_override_values_survive_mode_switches(session, assembly):
    target, _ = assembly
    values = dict(gap_mode="OVERRIDE", gap_strength=0.7, collagen_mode="UNIFORM", collagen=0.4)
    session.command("skin.contributor.configure", owner=target, values=values)
    assert skin_operations.effective_settings(session.document, target).gap_strength == 0.7
    session.command("skin.contributor.configure", owner=target, values=dict(gap_mode="INHERIT"))
    assert skin_operations.effective_settings(session.document, target).gap_strength == 1
    assert skin_operations.settings_for(session.document.skin, target).gap_strength == 0.7
    session.command("undo")
    assert skin_operations.effective_settings(session.document, target).gap_strength == 0.7


def test_reset_draft_defaults_is_one_undo_and_preserves_other_settings(session):
    skin = session.document.skin
    changed = replace(skin, envelope_settings=replace(EnvelopeSettings(), gap_strength=0.2))
    changed = replace(changed, contributors=(SkinContributor("saved", collagen=0.3),))
    session.replace_document(skin=changed)
    session.command("skin.envelope.reset")
    assert session.document.skin.envelope_settings == EnvelopeSettings()
    assert session.document.skin.contributors == changed.contributors
    session.command("undo")
    assert session.document.skin == changed


def test_fit_inspection_exposes_active_bones_and_moving_accuracy(session):
    identity = setup(session)
    result = fit(session, identity)
    report = skin_fit_results.inspect(session, result.id)["report"]
    assert report["active_bones"] == 1
    expected = max(r["moving_p95_percent_height"] for r in report["rows"] if not r["training"])
    assert report["moving_validation_p95"] == expected
