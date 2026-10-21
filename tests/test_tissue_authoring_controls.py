"""Authoring controls preserve shared construction, evaluation ownership and history."""

import numpy as np
import pytest

from anthroforge.application import tissue_stack_observation
from tests.test_tissue_parts_workflow import branched_tissue
from tests.test_tissue_stack_workflow import assembly, current
from tests.test_tissue_workflow import roundtrip


def sides(session, target):
    return session.document.object(target).parts


def prepared_sides(session):
    source, target, branch = branched_tissue(session)
    session.command("tissue.configure", target=target, changes=dict(both_sides=True))
    session.command("tissue.inflation", target=target, part=branch, changes=dict(amount=0.08))
    session.command("tissue.smoothing", target=target, part=branch, changes=dict(radius=0.12))
    session.wait()
    return source, target, branch


def test_copy_selected_side_preserves_sources_and_other_parts(session):
    source, target, branch = prepared_sides(session)
    original, before = session.document.object(source), sides(session, target)
    session.command("tissue.side.copy", target=target, part=branch, source="a", destination="b")
    session.wait()
    after = sides(session, target)
    assert after[0] == before[0] and after[1].a == before[1].a == after[1].b
    assert after[1].connector_width == before[1].connector_width
    assert after[1].connector_fullness == before[1].connector_fullness
    assert session.document.object(source) == original
    session.command("undo")
    assert sides(session, target) == before
    session.command("redo")
    assert sides(session, target) == after


def test_copy_all_sides_preserves_independent_branch_values_and_roundtrips(session, tmp_path):
    _, target, _ = prepared_sides(session)
    session.command("tissue.side.copy", target=target, source="a", destination="b", all_parts=True)
    session.wait()
    result = sides(session, target)
    assert all(part.a == part.b for part in result)
    assert result[0].a.inflation.amount != result[1].a.inflation.amount
    roundtrip(session, tmp_path / "copied.anthroforge")
    assert sides(session, target) == result


@pytest.mark.parametrize("changes", [dict(source="a", destination="a"), dict(all_parts=1)])
def test_invalid_copy_is_atomic(session, changes):
    _, target, _ = prepared_sides(session)
    before = session.document
    settings = dict(target=target, source="a", destination="b") | changes
    with pytest.raises(ValueError):
        session.command("tissue.side.copy", **settings)
    assert session.document == before


def grouped(session):
    _, first, second = assembly(session)
    before = session.document.object(second)
    session.command("tissue.configure", target=first, changes=dict(group="Front"))
    session.command("tissue.configure", target=second, changes=dict(group="Front"))
    session.wait(30)
    return first, second, before


def test_stacking_group_refreshes_pair_plan_without_rebuilding_inflation(session, tmp_path):
    _, second, before = grouped(session)
    item = session.document.object(second)
    assert not item.stack_plan.providers and item.group == "Front"
    assert item.intrinsic_result == before.intrinsic_result
    np.testing.assert_allclose(
        current(session, second), session.assets[item.intrinsic_result.asset].mesh.array(0)
    )
    roundtrip(session, tmp_path / "groups.anthroforge")
    assert session.document.object(second).group == "Front"


def test_clearing_group_restores_automatic_stacking_and_undo(session):
    first, second, _ = grouped(session)
    session.command("tissue.configure", target=second, changes=dict(group=""))
    session.wait(30)
    assert session.document.object(second).stack_plan.providers == (first,)
    session.command("undo")
    session.wait(30)
    assert not session.document.object(second).stack_plan.providers


def test_explicit_pair_remains_available_within_group(session):
    first, second, _ = grouped(session)
    session.command("tissue.stacking.relationship", target=second, other=first, mode="EXPLICIT")
    session.wait(30)
    assert session.document.object(second).stack_plan.providers == (first,)
    current(session, second)


def test_discovery_allowance_invalidates_observed_scope_and_preserves_intrinsic(session):
    _, first, second = assembly(session)
    before = session.document.object(first)
    scope = tissue_stack_observation.membership(session.document)
    session.command("tissue.stacking.configure", target=first, changes=dict(displacement=0.125))
    session.wait(30)
    assert tissue_stack_observation.membership(session.document) != scope
    after = session.document.object(first)
    assert after.intrinsic_result == before.intrinsic_result
    assert after.stack_settings.displacement == 0.125
    current(session, second)


@pytest.mark.parametrize("changes", [dict(group=" x "), dict(group=42), dict(group="x" * 257)])
def test_invalid_group_is_rejected_without_partial_edits(session, changes):
    _, first, _ = assembly(session)
    before = session.document
    with pytest.raises(ValueError):
        session.command("tissue.configure", target=first, changes=changes)
    assert session.document == before
