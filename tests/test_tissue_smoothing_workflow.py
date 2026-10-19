"""Smoothing settings use staged evaluation, accepted sources, persistence and undo."""

import numpy as np
import pytest

from tests.test_tissue_parts_workflow import branched_tissue
from tests.test_tissue_workflow import assembly, mesh, roundtrip


def test_smoothing_diagnostics_roundtrip_and_off_restores_exact_shape(session, tmp_path):
    _, source, target = assembly(session)
    original, points = session.document.object(source), mesh(session, target)
    session.command("tissue.smoothing", target=target, changes=dict(mode="HEIGHT"))
    session.wait()
    item = session.document.object(target)
    assert item.result.status == "ready" and item.diagnostics[0].stage == "rest"
    assert session.document.object(source) == original
    assert not np.array_equal(mesh(session, target), points)
    roundtrip(session, tmp_path / "smoothing.anthroforge")
    assert session.document.object(target).diagnostics == item.diagnostics
    session.command("tissue.smoothing", target=target, changes=dict(mode="OFF"))
    session.wait()
    np.testing.assert_array_equal(mesh(session, target), points)
    assert not [d for d in session.document.object(target).diagnostics if d.stage == "rest"]


def test_branch_side_smoothing_is_independent_and_undoable(session):
    _, target, branch = branched_tissue(session)
    session.command("tissue.configure", target=target, changes=dict(both_sides=True))
    session.wait()
    before = mesh(session, target)
    session.command(
        "tissue.smoothing", target=target, part=branch, side="b", changes=dict(mode="HEIGHT")
    )
    session.wait()
    item = session.document.object(target)
    reports = [d for d in item.diagnostics if d.stage == "rest"]
    assert item.result.status == "ready" and [(d.part, d.side) for d in reports] == [(branch, "b")]
    session.command("undo")
    session.wait()
    np.testing.assert_array_equal(mesh(session, target), before)


def test_unsupported_smoothing_combination_is_rejected_at_shared_boundary(session):
    _, _, target = assembly(session)
    session.command("tissue.inflation", target=target, changes=dict(mode="NORMAL"))
    with pytest.raises(ValueError, match="requires muscle grid"):
        session.command("tissue.smoothing", target=target, changes=dict(mode="HEIGHT"))
