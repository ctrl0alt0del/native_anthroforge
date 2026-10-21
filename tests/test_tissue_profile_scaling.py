"""Proportional profile edits change depth only and preserve undo and validation."""

import pytest

from anthroforge.native import tissue_parts
from tests.test_tissue_workflow import assembly, roundtrip


def profile(session, target):
    return session.document.object(target).parts[0].a.inflation.profile


def configured(session):
    _, source, target = assembly(session)
    data = dict(depths=[0.01, 0.04, 0.02, 0], peaks=[0.2, 0.4, 0.7, 0.6], direction="LOCAL")
    session.command(
        "tissue.inflation", target=target, changes=dict(mode="SECTION_PROFILE", profile=data)
    )
    session.wait()
    return source, target


def test_profile_scale_preserves_ratios_and_other_profile_settings(session, tmp_path):
    source, target = configured(session)
    before, original = profile(session, target), session.document.object(source)
    cursor = session.history.cursor
    session.command("tissue.profile.scale", target=target, factor=1.5)
    session.wait()
    after = profile(session, target)
    assert after.depths == pytest.approx((0.015, 0.06, 0.03, 0))
    assert_properties(before, after)
    assert session.document.object(source) == original and session.history.cursor == cursor + 1
    session.command("undo")
    assert profile(session, target) == before
    session.command("redo")
    roundtrip(session, tmp_path / "scaled.anthroforge")
    assert profile(session, target) == after


def assert_properties(before, after):
    assert after.peaks == before.peaks
    assert after.direction == before.direction
    assert after.roundness == before.roundness


@pytest.mark.parametrize("factor", [-1, float("nan"), float("inf"), 1000])
def test_invalid_profile_scale_keeps_original_state(session, factor):
    _, target = configured(session)
    before = session.document
    with pytest.raises(ValueError):
        session.command("tissue.profile.scale", target=target, factor=factor)
    assert session.document == before


def test_native_scaling_preserves_zero_stations_and_all_zero_fields(session):
    assert tissue_parts.scale_profile(session.engine, (0, 0, 0, 0), 2) == (0, 0, 0, 0)
    assert tissue_parts.scale_profile(session.engine, (0, 0.01, 0.03, 0.02), 0) == (0, 0, 0, 0)
    with pytest.raises(ValueError, match="four station"):
        tissue_parts.scale_profile(session.engine, (1, 2, 3), 2)
