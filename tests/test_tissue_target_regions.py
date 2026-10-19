"""Target-relative regions preserve source ownership and retained material attachment goals."""

from threading import Event

import numpy as np
import pytest

from anthroforge.application.resources import referenced
from tests.test_tissue_anchor_material import bound_to_second_side
from tests.test_tissue_routing import radial
from tests.test_tissue_workflow import roundtrip


def region_scene(session):
    bone, tissue = radial(session)
    other = session.command("import", path="examples/primitives/cube.obj", units=1.0, parent=bone)[
        "entity_id"
    ]
    session.wait()
    session.command("scp.transform", entity=other, values=[2, 0, 0, 0, 0, 0, 1, 1, 1])
    region = session.command("tissue.constraint.add", target=tissue, mask="ALL")
    session.wait()
    return tissue, region, other


def bind_region(session, tissue, region, parent, role=""):
    job = session.command(
        "tissue.constraint.bind", target=tissue, constraint=region, parent=parent, role=role
    )
    session.wait()
    row = next(j for j in session.scheduler.jobs if j.id == job)
    assert row.state == "succeeded", row.error
    item = session.document.object(tissue)
    assert item.intrinsic_result.status == "ready", item.intrinsic_result.error
    return next(r for r in item.constraints if r.id == region)


def positions(session, tissue):
    item = session.document.object(tissue)
    assert item.intrinsic_result.status == "ready", item.intrinsic_result.error
    return session.assets[item.intrinsic_result.asset].mesh.array(0).copy()


def test_target_motion_updates_only_intrinsic_and_preserves_sources(session, tmp_path):
    tissue, region, parent = region_scene(session)
    source = session.document.object(session.document.object(tissue).source)
    opening, cursor = positions(session, tissue), session.history.cursor
    binding = bind_region(session, tissue, region, parent)
    assert session.history.cursor == cursor + 1
    item = session.document.object(tissue)
    np.testing.assert_allclose(positions(session, tissue), opening, atol=1e-10)
    session.command("scp.transform", entity=parent, values=[2.2, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(positions(session, tissue), opening + [0.2, 0, 0], atol=1e-10)
    assert session.document.object(tissue).rest_result == item.rest_result
    assert session.document.object(source.id) == source
    saved_binding(session, tissue, binding, tmp_path)


def saved_binding(session, tissue, binding, location):
    keys = referenced(session.document)
    assert binding.binding_asset in keys["bindings"] and binding.material_asset in keys["meshes"]
    roundtrip(session, location / "target-region.anthroforge")
    assert binding in session.document.object(tissue).constraints
    assert session.resources.bindings[binding.binding_asset].bytes > 0


def test_binding_undo_redo_and_explicit_unlink_restore_source_goals(session):
    tissue, region, parent = region_scene(session)
    binding = bind_region(session, tissue, region, parent)
    session.navigate(-1)
    assert session.document.object(tissue).constraints[0].reference is None
    session.navigate(1)
    session.wait()
    assert session.document.object(tissue).constraints[0].reference == binding.reference
    session.command("tissue.constraint.unlink", target=tissue, constraint=region)
    session.wait()
    assert session.document.object(tissue).constraints[0].reference is None
    reject_implicit_rebind(session, tissue, region, parent)


def reject_implicit_rebind(session, tissue, region, parent):
    with pytest.raises(ValueError, match="explicit rebind"):
        session.command(
            "tissue.constraint.update",
            target=tissue,
            constraint=region,
            changes=dict(reference=parent),
        )


def test_incompatible_rest_domain_fails_without_implicit_rebind(session):
    tissue, region, parent = region_scene(session)
    binding = bind_region(session, tissue, region, parent)
    before = session.document.object(tissue).intrinsic_result.asset
    session.command("tissue.configure", target=tissue, changes=dict(resolution=12))
    session.wait()
    item = session.document.object(tissue)
    assert item.intrinsic_result.status == "failed" and "rebind" in item.intrinsic_result.error
    assert item.intrinsic_result.asset == before and binding in item.constraints
    rebound = bind_region(session, tissue, region, parent)
    assert rebound.topology != binding.topology and rebound.binding_asset != binding.binding_asset


def test_target_region_cannot_move_exact_structural_backing(session):
    from tests.test_tissue_relaxation import shell

    tissue = shell(session)
    parent = other_cube(session)
    session.wait()
    region = session.command("tissue.constraint.add", target=tissue, mask="BACKING")
    session.wait()
    bind_region(session, tissue, region, parent)
    before = session.document.object(tissue).intrinsic_result.asset
    session.command("scp.transform", entity=parent, values=[0.2, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    result = session.document.object(tissue).intrinsic_result
    assert result.status == "failed" and "Contradictory" in result.error
    assert result.asset == before


def other_cube(session):
    root = session.document.entities[0].id
    return session.command("import", path="examples/primitives/cube.obj", units=1.0, parent=root)[
        "entity_id"
    ]


def held_capture(monkeypatch):
    from anthroforge.application import tissue_region_goals

    entered, release = Event(), Event()
    original = tissue_region_goals.capture

    def capture(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(tissue_region_goals, "capture", capture)
    return entered, release


def test_undo_cancels_capture_and_redo_restarts_one_authored_binding(session, monkeypatch):
    tissue, region, parent = region_scene(session)
    entered, release = held_capture(monkeypatch)
    session.command("tissue.constraint.bind", target=tissue, constraint=region, parent=parent)
    session.scheduler.tick()
    try:
        assert entered.wait(2)
        session.navigate(-1)
    finally:
        release.set()
    session.wait()
    assert session.document.object(tissue).constraints[0].reference is None
    session.navigate(1)
    session.wait()
    assert session.document.object(tissue).constraints[0].reference.target == parent


def test_constraint_target_material_survives_tissue_compaction(session):
    parent, anchor = bound_to_second_side(session)
    tissue = session.command("tissue.create", source=anchor.id, preset="CUSTOM")
    session.wait()
    region = session.command("tissue.constraint.add", target=tissue, mask="ALL")
    session.wait()
    binding = bind_region(session, tissue, region, parent, "TISSUE_FINAL")
    before = positions(session, tissue)
    session.command("tissue.inflation", target=parent, side="a", changes=dict(enabled=False))
    session.wait()
    np.testing.assert_allclose(positions(session, tissue), before, atol=1e-9)
    assert binding in session.document.object(tissue).constraints


def test_target_offset_uses_captured_surface_normal(session):
    tissue, region, parent = region_scene(session)
    session.command("scp.transform", entity=parent, values=[2, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait()
    bind_region(session, tissue, region, parent)
    before = positions(session, tissue)
    session.command(
        "tissue.constraint.update", target=tissue, constraint=region, changes=dict(offset=0.1)
    )
    session.wait()
    delta = positions(session, tissue) - before
    np.testing.assert_allclose(np.linalg.norm(delta, axis=1), 0.1, atol=1e-10)
    assert np.max(np.abs(delta[:, 0])) > 0.07


def capture_across_parent_edit(session, monkeypatch):
    tissue, region, parent = region_scene(session)
    before = positions(session, tissue)
    _, release = held_capture(monkeypatch)
    session.command("tissue.constraint.bind", target=tissue, constraint=region, parent=parent)
    origin = session.history.cursor
    try:
        session.command("scp.transform", entity=parent, values=[2.2, 0, 0, 0, 0, 0, 1, 1, 1])
    finally:
        release.set()
    session.wait()
    return tissue, parent, origin, before


def test_historical_binding_captures_its_own_parent_pose(session, monkeypatch):
    tissue, parent, origin, before = capture_across_parent_edit(session, monkeypatch)
    old = session.history.entries[origin].document.object(tissue)
    assert old.constraints[0].reference is None
    session.navigate(-1)
    session.wait()
    assert session.document.object(tissue).constraints[0].reference.target == parent
    np.testing.assert_allclose(positions(session, tissue), before, atol=1e-10)
    session.navigate(1)
    session.wait()
    np.testing.assert_allclose(positions(session, tissue), before, atol=1e-10)
    verify_future_capture(session, tissue, parent, before)


def verify_future_capture(session, tissue, parent, before):
    session.command("scp.transform", entity=parent, values=[2.3, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(positions(session, tissue), before + [0.1, 0, 0], atol=1e-10)


def test_region_binding_memory_has_document_and_history_owners(session, tmp_path):
    from anthroforge.profiling.resource_inventory import inventory
    from tests.test_profile_diagnostics import report

    tissue, region, parent = region_scene(session)
    binding = bind_region(session, tissue, region, parent)
    size = session.resources.bindings[binding.binding_asset].bytes
    session.command("profile.start", memory_mib=16)
    evidence = inventory(session.profiler, session.profiler.resources.owners())
    owners = evidence["by_kind"]["attachments"]["owners"]
    assert owners["document"]["bytes"] >= size and owners["history"]["bytes"] >= size
    data = report(session, tmp_path / "region-memory.afprofile.zip")
    assert data["manifest.json"]["complete"], data["manifest.json"]["losses"]
