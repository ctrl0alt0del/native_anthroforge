"""Attached branches retain accepted part identities, independent settings and undo."""

import numpy as np

from tests.conftest import CUBE
from tests.test_fiber_creation import bind
from tests.test_junction_workflow import reference
from tests.test_surface_branches import source_curves
from tests.test_surface_workflow import surface
from tests.test_tissue_workflow import assembly as ordinary
from tests.test_tissue_workflow import mesh, roundtrip


def attached_curves(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    keys = [bind(session, bone, key).id for key in source_curves(session)]
    for index, key in enumerate(keys[2:], 1):
        session.command(
            "junction.create",
            source=reference(session, key),
            targets=[reference(session, keys[0], index)],
        )
    session.wait()
    return keys


def branched_tissue(session):
    keys = attached_curves(session)
    base = surface(session, keys[:2])
    branch = session.command("surface.branch.add", target=base, boundary=keys[0], curves=keys[2:])
    session.wait()
    target = session.command("tissue.create", source=base)
    session.command("tissue.configure", target=target, changes=dict(stacking=False))
    session.wait()
    return base, target, branch


def test_branch_parts_accept_independent_settings_and_preserve_shared_source(session, tmp_path):
    source, target, branch = branched_tissue(session)
    before = mesh(session, target)
    source_record = session.document.object(source)
    session.command("tissue.inflation", target=target, part=branch, changes=dict(amount=0.15))
    session.wait()
    item = session.document.object(target)
    assert item.base_state.parts == ("main", branch)
    assert [p.id for p in item.parts] == ["main", branch]
    assert item.parts[0].a.inflation.amount != item.parts[1].a.inflation.amount
    assert session.document.object(source) == source_record
    assert not np.array_equal(mesh(session, target), before)
    roundtrip(session, tmp_path / "branched-tissue.anthroforge")
    assert session.document.object(target) == item


def test_manual_source_retains_accepted_branch_ids_until_publication(session):
    source, target, branch = branched_tissue(session)
    before = session.document.object(target).base_state.parts
    session.command("update_mode", entity=source, mode="MANUAL")
    session.command("surface.branch.remove", target=source, branch=branch)
    session.wait()
    session.command("tissue.inflation", target=target, changes=dict(amount=0.06))
    session.wait()
    assert session.document.object(target).base_state.parts == before
    assert session.document.object(target).result.status == "ready"
    session.command("evaluate", entities=[source])
    session.wait()
    assert session.document.object(target).base_state.parts == ("main",)


def test_two_sides_have_distinct_settings_and_roundtrip(session, tmp_path):
    _, target, branch = branched_tissue(session)
    session.command("tissue.configure", target=target, changes=dict(both_sides=True))
    session.command(
        "tissue.inflation", target=target, part=branch, side="b", changes=dict(amount=0.09)
    )
    session.wait()
    before = mesh(session, target)
    item = session.document.object(target)
    assert len(before) > session.assets[item.base_result.asset].mesh.counts[0]
    roundtrip(session, tmp_path / "envelope.anthroforge")
    np.testing.assert_array_equal(mesh(session, target), before)


def test_profile_initializes_once_and_reset_is_undoable(session):
    _, _, target = ordinary(session)
    session.command(
        "tissue.inflation", target=target, changes=dict(amount=0.08, mode="SECTION_PROFILE")
    )
    session.wait()
    first = session.document.object(target).parts[0].a.inflation.profile
    assert first.initialized and first.depths == (0.04, 0.08, 0.08, 0.04)
    session.command(
        "tissue.inflation", target=target, changes=dict(mode="DISTRIBUTED", amount=0.15)
    )
    session.command("tissue.inflation", target=target, changes=dict(mode="SECTION_PROFILE"))
    assert session.document.object(target).parts[0].a.inflation.profile == first
    reset_and_undo(session, target, first)


def reset_and_undo(session, target, first):
    session.command("tissue.profile.reset", target=target)
    session.wait()
    depths = session.document.object(target).parts[0].a.inflation.profile.depths
    assert depths == (0.075, 0.15, 0.15, 0.075)
    session.command("undo")
    assert session.document.object(target).parts[0].a.inflation.profile == first


def test_control_reset_and_connector_changes_use_accepted_part_without_source_mutation(session):
    source, target, branch = branched_tissue(session)
    before = session.document.object(source)
    session.command("tissue.inflation", target=target, part=branch, changes=dict(mode="CTRL_POINT"))
    session.command("tissue.control.reset", target=target, part=branch)
    session.command("tissue.connector", target=target, part=branch, width=0.3, fullness=0.02)
    session.wait()
    item = session.document.object(target)
    assert len(item.parts[1].a.inflation.control) == 3 and item.parts[1].connector_width == 0.3
    assert item.result.status == "ready" and session.document.object(source) == before
