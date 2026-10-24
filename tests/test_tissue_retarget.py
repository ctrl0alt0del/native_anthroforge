"""Retargeting preserves identities and reviews cross-family losses before one coherent edit."""

import pytest

from anthroforge.core.tissue_revisions import PHASES
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve, surface
from tests.test_tissue_workflow import assembly


def anchor(session, parent):
    point = session.command("construction.point.create", position=[0, 0, 0.7])
    result = session.command("anchor.create", source=point, parent=parent)
    session.wait(5)
    return result["object_id"]


def assess(session, target, source):
    result = session.command("tissue.source.replace.assess", target=target, source=source)
    session.wait(10)
    state = session.command("tissue.source.replace.status")
    assert state["state"] == "ready", state
    return result["token"], state


def apply(session, token, state):
    session.command(
        "tissue.source.replace.apply", token=token, approved=[c["key"] for c in state["changes"]]
    )
    session.wait(10)


def test_surface_to_anchor_reviews_mode_changes_without_changing_source(session):
    bone, source, target = assembly(session)
    new_source = anchor(session, bone)
    before, cursor = session.document.object(target), session.history.cursor
    token, state = assess(session, target, new_source)
    assert session.document.object(target) == before and session.history.cursor == cursor
    assert any(c["key"].startswith("mode:") for c in state["changes"])
    with pytest.raises(ValueError, match="Explicitly approve"):
        session.command("tissue.source.replace.apply", token=token)
    apply(session, token, state)
    verify_radial(session, target, new_source, source, before)
    assert session.history.cursor == cursor + 1


def verify_radial(session, target, new_source, source, before):
    item = session.document.object(target)
    assert item.source == new_source and item.parts[0].a.inflation.mode == "RADIAL"
    assert item.result.status == "ready", item.result.error
    assert source in session.document.registry.records
    assert item.classification == before.classification


def replacement_membrane(session, bone):
    fibers = [bind(session, bone, curve(session, y)).id for y in (0.2, 0.6)]
    return surface(session, fibers, strips=6)


def test_compatible_membrane_preserves_settings_and_reuses_prepared_stages(session):
    bone, source, target = assembly(session)
    new_source = replacement_membrane(session, bone)
    before = session.document.object(target)
    token, state = assess(session, target, new_source)
    existing = set(session.scheduler.registry.by_id)
    apply(session, token, state)
    item = session.document.object(target)
    assert item.source == new_source and item.parts == before.parts
    assert item.result.status == "ready", item.result.error
    assert_no_rebuild(session, target, existing)
    session.command("undo")
    assert session.document.object(target).source == source


def test_retarget_rejects_stale_decisions(session):
    bone, _, target = assembly(session)
    token, state = assess(session, target, anchor(session, bone))
    session.command("tissue.inflation", target=target, changes=dict(amount=0.03))
    session.wait(10)
    before = session.document
    with pytest.raises(ValueError, match="current successful|definitions changed"):
        apply(session, token, state)
    assert session.document == before


def assert_no_rebuild(session, target, existing):
    added = [job for key, job in session.scheduler.registry.by_id.items() if key not in existing]
    assert not [
        j for j in added if any(p.owner == target and p.output in PHASES for p in j.provides)
    ]


def final_anchor(session, target, role="TISSUE_FINAL"):
    point = session.command("construction.point.create", position=[0, 0.2, 0.1])
    result = session.command("anchor.create", source=point, parent=target, role=role)
    session.wait(5)
    return result["object_id"]


def test_final_surface_binding_is_reviewed_and_preserves_reference_role(session):
    bone, _, target = assembly(session)
    attached = final_anchor(session, target)
    before = session.document.object(attached)
    token, state = assess(session, target, anchor(session, bone))
    assert any(row["target"] == attached for row in state["changes"])
    apply(session, token, state)
    current = session.document.object(attached)
    assert current.result.status == "ready", current.result.error
    assert current.binding.reference == before.binding.reference


def test_unavailable_base_role_never_silently_changes_to_final(session):
    bone, _, target = assembly(session)
    attached = final_anchor(session, target, "TISSUE_BASE")
    new_source = anchor(session, bone)
    before = session.document
    session.command("tissue.source.replace.assess", target=target, source=new_source)
    session.wait(10)
    state = session.command("tissue.source.replace.status")
    assert state["state"] == "failed", state
    assert "base" in state["error"].lower(), state
    assert session.document == before
    assert session.document.object(attached).binding.reference.role == "TISSUE_BASE"


def test_cross_family_field_loss_requires_review(session):
    from anthroforge.application.tissue_fields import domain

    bone, _, target = assembly(session)
    session.command("tissue.inflation", target=target, changes=dict(mode="NORMAL"))
    session.wait(5)
    count, _ = domain(session.resources, session.document.object(target), "BASE")
    session.command("tissue.field.set", target=target, name="Custom", values=[0.3] * count)
    session.wait(5)
    token, state = assess(session, target, anchor(session, bone))
    assert any(c["key"] == "field:Custom" for c in state["changes"])
    assert session.document.object(target).fields
    apply(session, token, state)
    assert not session.document.object(target).fields


def test_retarget_roundtrip_preserves_all_accepted_stages(session, tmp_path):
    bone, _, target = assembly(session)
    source = anchor(session, bone)
    token, state = assess(session, target, source)
    apply(session, token, state)
    current = session.document.object(target)
    output = tmp_path / "retarget.anthroforge"
    session.command("save", path=str(output), blocked_policy="wait")
    session.command("open", path=str(output))
    session.wait(5)
    assert session.document.object(target).source == source
    assert session.document.object(target).final_result.asset == current.final_result.asset
    assert session.document.object(target).base_state.kind == "POINT"


def test_anchor_to_fiber_retarget_uses_profile_and_preserves_old_sources(session):
    bone, membrane, target = assembly(session)
    point = anchor(session, bone)
    apply(session, *assess(session, target, point))
    fiber = session.document.object(membrane).curves[0].curve
    apply(session, *assess(session, target, fiber))
    item = session.document.object(target)
    assert item.source == fiber and item.base_state.kind == "CURVE"
    assert item.parts[0].a.inflation.mode == "PROFILE" and item.result.status == "ready"
    assert (
        point in session.document.registry.records and membrane in session.document.registry.records
    )


def test_compatible_source_preserves_custom_material_field(session):
    from anthroforge.application.tissue_fields import domain

    bone, _, target = assembly(session)
    session.command("tissue.inflation", target=target, changes=dict(mode="NORMAL"))
    session.wait(5)
    count, _ = domain(session.resources, session.document.object(target), "BASE")
    session.command("tissue.field.set", target=target, name="Custom", values=[0.3] * count)
    session.wait(5)
    before = session.document.object(target).fields
    token, state = assess(session, target, replacement_membrane(session, bone))
    assert not any(row["key"] == "field:Custom" for row in state["changes"])
    apply(session, token, state)
    assert session.document.object(target).fields == before


def test_pending_manual_source_uses_accepted_path_with_provenance(session):
    bone, _, target = assembly(session)
    fiber = bind(session, bone, curve(session, 0.2)).id
    session.command("update_mode", entity=fiber, mode="MANUAL")
    item = session.document.object(fiber)
    session.command(
        "curve.point.update", curve=fiber, point=item.points[1].id, position=[0.5, 0.2, 0.1]
    )
    accepted = session.document.object(fiber).result.asset
    apply(session, *assess(session, target, fiber))
    result = session.document.object(target)
    assert result.base_result.asset == accepted and fiber in result.base_result.pending
    assert result.result.status == "ready", result.result.error
