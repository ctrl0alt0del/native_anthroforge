"""Existing-tissue defaults never overwrite user-owned construction or relationship settings."""

from dataclasses import asdict

import pytest

from anthroforge.application.tissue_codec import constraint
from anthroforge.application.tissue_fields import domain
from tests.test_tissue_presets import source


def create(session):
    key = session.command("tissue.create", source=source(session, "LAYER"), preset="LAYER")
    session.wait(10)
    return key


def custom_region(session, target, **values):
    return session.command(
        "tissue.constraint.add", target=target, mask="ALL", mode="SOFT", strength=0.25, **values
    )


def test_apply_preserves_custom_settings_and_one_undo(session):
    target = create(session)
    region = custom_region(session, target)
    session.command("tissue.inflation", target=target, changes=dict(amount=0.1))
    session.wait(10)
    before, cursor = session.document.object(target), session.history.cursor
    session.command("tissue.preset.apply", target=target, preset="POUCH")
    session.wait(10)
    item = session.document.object(target)
    verify_preserved(before, item, region)
    assert item.parts[0].a.inflation.amount == 0.62
    assert item.relaxation.mode == "STATIC_PBD" and item.result.status == "ready", item.result.error
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.object(target).parts == before.parts


def verify_preserved(before, after, region):
    for name in ("source", "classification", "fields", "crop", "stacking", "stack_settings"):
        assert getattr(before, name) == getattr(after, name)
    assert next(row for row in after.constraints if row.id == region).origin == "CUSTOM"
    assert all(
        row.id not in {r.id for r in before.constraints if r.origin == "PRESET"}
        for row in after.constraints
    )


def test_editing_preset_constraint_promotes_it_to_custom(session):
    target = create(session)
    row = session.document.object(target).constraints[0]
    assert row.origin == "PRESET"
    session.command(
        "tissue.constraint.update", target=target, constraint=row.id, changes=dict(feather=0.1)
    )
    session.wait(10)
    session.command("tissue.preset.apply", target=target, preset="CUSTOM")
    item = session.document.object(target)
    assert [r.id for r in item.constraints] == [row.id]
    assert item.constraints[0].origin == "CUSTOM" and item.constraints[0].feather == 0.1


def test_conflicting_custom_region_rejects_without_overwriting(session):
    target = create(session)
    session.command("tissue.constraint.add", target=target, mask="BOUNDARY", offset=0.1)
    session.wait(10)
    before, cursor = session.document, session.history.cursor
    with pytest.raises(ValueError, match="conflicts with a custom"):
        session.command("tissue.preset.apply", target=target, preset="POUCH")
    assert session.document == before and session.history.cursor == cursor


def test_legacy_constraint_is_conservatively_custom_and_tags_roundtrip():
    legacy = constraint(dict(mask="BACKING"))
    assert legacy.origin == "CUSTOM"
    assert constraint(asdict(legacy)) == legacy
    with pytest.raises(ValueError, match="origin"):
        constraint(dict(mask="BACKING", origin="GUESS_FROM_NAME"))


def test_custom_weights_survive_preset_and_package_roundtrip(session, tmp_path):
    target = create(session)
    count, _ = domain(session.resources, session.document.object(target), "BASE")
    session.command("tissue.field.set", target=target, name="Custom weight", values=[0.3] * count)
    session.wait(10)
    field = session.document.object(target).fields[0]
    session.command("tissue.preset.apply", target=target, preset="POUCH")
    session.wait(10)
    assert session.document.object(target).fields == (field,)
    output = tmp_path / "preset.anthroforge"
    session.command("save", path=str(output), blocked_policy="wait")
    session.command("open", path=str(output))
    assert session.document.object(target).fields == (field,)
    assert all(r.origin == "PRESET" for r in session.document.object(target).constraints)
