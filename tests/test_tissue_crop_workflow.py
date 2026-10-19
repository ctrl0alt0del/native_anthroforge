"""Crop stages preserve accepted rest, handle empty output, locks and save/undo."""

import numpy as np
import pytest

from anthroforge.application import surface_providers
from anthroforge.core.surface_references import SurfaceReference
from tests.test_tissue_workflow import assembly, mesh, roundtrip


@pytest.mark.parametrize("envelope", [False, True])
def test_crop_does_not_reinflate_and_can_be_disabled(session, envelope):
    _, source, target = assembly(session)
    session.command("tissue.configure", target=target, changes=dict(both_sides=envelope))
    session.wait()
    item, before = session.document.object(target), mesh(session, target)
    session.command("tissue.crop", target=target, changes=dict(enabled=True, origin=[0.5, 0, 0]))
    session.wait()
    after = session.document.object(target)
    assert after.result.status == "ready" and after.rest_result == item.rest_result
    assert not np.array_equal(mesh(session, target), before)
    assert session.document.object(source).result.asset
    session.command("tissue.crop", target=target, changes=dict(enabled=False))
    session.wait()
    np.testing.assert_array_equal(mesh(session, target), before)


def test_empty_crop_roundtrip_and_final_provider_reports_empty(session, tmp_path):
    _, _, target = assembly(session)
    session.command("tissue.crop", target=target, changes=dict(enabled=True, origin=[100, 0, 0]))
    session.wait()
    item = session.document.object(target)
    assert item.result.status == "ready" and mesh(session, target).shape == (0, 3)
    roundtrip(session, tmp_path / "empty.anthroforge")
    assert session.document.object(target) == item
    require_empty_provider(session, target)
    session.command("tissue.crop", target=target, changes=dict(enabled=False))
    session.wait()
    assert len(mesh(session, target)) > 0


def require_empty_provider(session, target):
    with pytest.raises(ValueError, match="is empty"):
        surface_providers.get(
            session.engine,
            session.document,
            session.assets,
            SurfaceReference(target, "TISSUE_FINAL"),
        )


def test_crop_undo_preserves_previous_geometry_and_source(session):
    _, source, target = assembly(session)
    source_record, before = session.document.object(source), mesh(session, target)
    session.command("tissue.crop", target=target, changes=dict(enabled=True, origin=[0.5, 0, 0]))
    session.wait()
    session.command("undo")
    session.wait()
    np.testing.assert_array_equal(mesh(session, target), before)
    assert session.document.object(source) == source_record


def test_crop_rejects_unqualified_construction_combination(session):
    _, _, target = assembly(session)
    session.command("tissue.inflation", target=target, changes=dict(mode="NORMAL"))
    with pytest.raises(ValueError, match="requires muscle grid"):
        session.command(
            "tissue.crop", target=target, changes=dict(enabled=True, origin=[0.5, 0, 0])
        )


def test_crop_topology_lock_names_incoming_anchor_and_unlocks_on_removal(session):
    _, _, target = assembly(session)
    source = session.command("construction.point.create", position=[0.5, 0.2, 0.5])
    binding = session.command("anchor.create", source=source, parent=target, role="TISSUE_FINAL")
    session.wait()
    anchor = binding["object_id"]
    assert anchor in session.document.registry.records
    with pytest.raises(ValueError, match=anchor):
        session.command("tissue.crop", target=target, changes=dict(enabled=True))
    session.command("object.delete", target=anchor)
    session.command("tissue.crop", target=target, changes=dict(enabled=True, origin=[0.5, 0, 0]))
    session.wait()
    assert session.document.object(target).result.status == "ready"
