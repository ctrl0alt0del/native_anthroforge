"""Pending builder records cannot contaminate another builder's accepted inputs."""

from dataclasses import asdict, replace

import pytest

from anthroforge.application import skin_builder_codec, skin_codec, skin_inputs, skin_pipeline
from anthroforge.application import skin_builder_configuration as builders
from anthroforge.core.skin import Skin, SkinContributor
from anthroforge.core.skin_draft import AppliedDraftConfiguration, DraftSettings, configuration


def select(skin, name):
    return replace(skin, draft_settings=replace(skin.draft_settings, backend=name))


def test_inactive_field_settings_do_not_change_avbd_dependencies(session):
    skin = select(Skin(), "AVBD")
    initial = replace(session.document, skin=skin)
    changed = builders.configure(skin, "FIELD", dict(gap_strength=0.13))
    changed, _ = builders.contributor(changed, "bone", dict(collagen=0.2))
    current = replace(initial, skin=changed)
    assert skin_inputs.envelope(initial) == skin_inputs.envelope(current)
    assert skin_inputs.build_signature(initial) == skin_inputs.build_signature(current)
    assert builders.decode(changed).plan == "{}"


def test_inactive_invalid_parameters_are_not_validated_by_another_builder():
    invalid = configuration("FIELD", dict(settings=dict(gap_strength=99)))
    skin = Skin(draft_settings=DraftSettings("AVBD", (invalid,)))
    assert builders.decode(skin).plan == "{}"
    assert builders.retained(skin) == set()
    with pytest.raises(ValueError):
        builders.decode(skin, "FIELD")


def test_inactive_avbd_settings_do_not_enter_field_dependencies_or_validation(session):
    initial = session.document
    invalid = configuration("AVBD", dict(plan="invalid numerical plan"))
    skin = replace(initial.skin, draft_settings=DraftSettings("FIELD", (invalid,)))
    changed = replace(initial, skin=skin)
    assert builders.decode(changed.skin).settings.gap_strength == 1
    assert skin_inputs.envelope(initial) == skin_inputs.envelope(changed)
    assert skin_pipeline.builder_key(initial) == skin_pipeline.builder_key(changed)


def test_automatic_capture_uses_applied_record_and_preserves_pending_edits(session):
    applied = configuration("FIELD", dict(settings=dict(gap_strength=0.2)))
    skin = Skin(applied_draft=AppliedDraftConfiguration(applied, 1))
    skin = builders.configure(select(skin, "AVBD"), "FIELD", dict(gap_strength=0.6))
    doc = replace(session.document, skin=skin)
    captured = builders.projected(doc, builders.automatic(skin))
    assert builders.decode(captured.skin).settings.gap_strength == 0.2
    assert builders.decode(doc.skin, "FIELD").settings.gap_strength == 0.6
    assert doc.skin.draft_settings.backend == "AVBD"


def test_legacy_assets_preserve_unknown_provenance_and_frozen_migration_settings():
    legacy = dict(envelope_settings=dict(gap_strength=0.4), envelope=dict(asset="old"))
    legacy["contributors"] = [dict(owner="bone", collagen=0.3, build_mode="FOLLOW")]
    skin = skin_codec.decode(legacy)
    assert skin.applied_draft is None and skin.update_mode == "DRAFT"
    assert builders.decode(skin, "FIELD").contributors[0].collagen == 0.3
    assert builders.decode(skin, "AVBD").contributors[0].build_mode == "FOLLOW"
    edited = builders.configure(skin, "FIELD", dict(gap_strength=0.8))
    assert builders.automatic(edited) == skin.migration_draft
    assert skin_codec.decode(skin_builder_codec.encode(edited)) == edited


def test_builder_record_serialization_preserves_applied_paint_resource():
    skin, _ = builders.contributor(Skin(), "bone", dict(painted="paint", collagen_mode="PAINTED"))
    applied = AppliedDraftConfiguration(skin.draft_settings.configuration(), 1)
    skin, _ = builders.contributor(skin, "bone", dict(painted="new-paint"))
    skin = replace(skin, applied_draft=applied)
    assert builders.retained(skin) == {"paint", "new-paint"}
    assert skin_codec.decode(skin_builder_codec.encode(skin)) == skin
    assert not {"collagen", "gap_strength", "build_mode"} & asdict(SkinContributor("bone")).keys()


def test_unknown_contributor_fields_are_rejected():
    with pytest.raises(TypeError, match="unrecognized"):
        skin_codec.decode(dict(contributors=[dict(owner="bone", unrecognized=1)]))
