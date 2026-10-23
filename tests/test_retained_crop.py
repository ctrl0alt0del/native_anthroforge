"""Material cuts retain their reference across deformation, history and storage."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import geometry_ownership, tissue_materials
from tests.test_tissue_workflow import assembly, mesh, roundtrip


def cropped(session):
    bone, _, tissue = assembly(session)
    session.command("tissue.crop", target=tissue, changes=dict(enabled=True, origin=(0.4, 0, 0)))
    session.wait()
    assert not session.scheduler.errors
    return bone, tissue


def move(session, bone, x):
    session.command("scp.transform", entity=bone, values=[x, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    assert not session.scheduler.errors


def test_cut_moves_with_material_and_survives_reopening(session, tmp_path):
    bone, target = cropped(session)
    before = mesh(session, target)
    reference = session.document.object(target).intrinsic_material.crop_base
    move(session, bone, 0.5)
    np.testing.assert_allclose(mesh(session, target), before + [0.5, 0, 0], atol=1e-9)
    geometry_ownership.collect(session)
    assert reference in session.assets
    roundtrip(session, tmp_path / "material-cut.anthroforge")
    assert session.document.object(target).intrinsic_material.crop_base == reference
    move(session, bone, 0)
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-9)


def test_plane_edit_defines_new_cut_and_undo_restores_previous_reference(session):
    bone, target = cropped(session)
    move(session, bone, 0.5)
    before = session.document.object(target).intrinsic_material
    session.command("tissue.crop", target=target, changes=dict(origin=(0.8, 0, 0)))
    session.wait()
    current = session.document.object(target).intrinsic_material
    assert current.crop_base == current.base and current.crop_base != before.crop_base
    session.command("undo")
    session.wait()
    assert session.document.object(target).intrinsic_material.crop_base == before.crop_base


def test_older_accepted_cut_uses_its_own_base_not_new_rest(session):
    bone, target = cropped(session)
    before = session.document.object(target).intrinsic_material
    move(session, bone, 0.5)
    current = session.document.object(target)
    legacy = replace(current, intrinsic_material=replace(before, crop_base=""))
    assert legacy.rest_material.base != before.base
    assert tissue_materials.crop_base(legacy) == before.base


def test_retained_material_cut_survives_changed_source_sampling(session):
    from anthroforge.core.tissue_settings import TissueCrop, TissuePart
    from anthroforge.native import construction, tissue_crop, tissue_parts
    from tests.test_adaptive_material_frames import loft

    reference = loft(session.engine, [0, 0.5, 1])
    base = loft(session.engine, [0, 0.2, 0.5, 0.8, 1])
    base = construction.deformed(base, base.array(0) + [0.3, 0, 0])
    own = tissue_parts.evaluate(base, (TissuePart(),), "a", False)
    crop = TissueCrop(True, (0.4, 0, 0))
    output = tissue_crop.retained(reference, base, own, crop)
    assert output.counts[0] and output.array(0)[:, 0].min() == pytest.approx(0.7)
    assert output.array(0)[:, 0].max() == pytest.approx(1.3)
