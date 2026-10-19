"""Retained locations survive output compaction and clipping without nearest recapture."""

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissueCrop
from anthroforge.native import (
    construction,
    material_bindings,
    point_attachments,
    tissue_crop,
    tissue_domain,
    tissue_parts,
)
from anthroforge.native.mesh import NativeCancellation
from tests.test_tissue_branches import CASES, inputs
from tests.test_tissue_crops import CASES as CROPS
from tests.test_tissue_crops import source as crop_source
from tests.test_tissue_envelopes import side

IDENTITY = np.eye(4).ravel()


def records(mesh, triangle=0):
    record = np.zeros((1, 28))
    record[0, :3], record[0, 3:6], record[0, 6:9] = mesh.array(3)[triangle], 1 / 3, -1
    return record


def resolved(mesh, row):
    return point_attachments.resolve(mesh.engine, [mesh.handle], [IDENTITY], [0], row)[0]


def side_triangle(mesh, side):
    data, _ = tissue_domain.arrays(mesh)
    start = 9 + data[5] + data[7]
    sides = data[start : start + data[5]]
    return next(i for i, tri in enumerate(mesh.array(3)) if (sides[tri] == side).all())


@pytest.mark.parametrize("disabled", ["a", "b", "both"])
def test_material_vertices_keep_side_identity_when_envelope_compacts(session, disabled):
    base, parts = inputs(session, CASES[0])
    a, b = side(base, parts, False, False), side(base, parts, True, False)
    original = tissue_parts.compose(a, b, False)
    changed = tissue_parts.compose(
        side(base, parts, False, disabled != "b"), side(base, parts, True, disabled != "a"), False
    )
    row = records(original, side_triangle(original, 2))
    adapter = material_bindings.resolve(original, changed, row)
    assert not adapter.prepared
    assert np.isfinite(resolved(adapter, row)).all()
    if disabled == "a":
        np.testing.assert_allclose(resolved(adapter, row), resolved(original, row), atol=1e-10)


def test_cropped_material_resolves_on_expanded_surface_without_moving(session):
    base, own = crop_source(session, CROPS[0])
    plane = TissueCrop(enabled=True, **CROPS[0]["plane"])
    clipped = tissue_crop.evaluate(base, own, plane)
    row = records(clipped, clipped.counts[3] // 2)
    adapter = material_bindings.resolve(clipped, own, row)
    np.testing.assert_allclose(resolved(adapter, row), resolved(clipped, row), atol=1e-9)


def test_lost_material_location_and_cancel_fail_explicitly(session):
    base, own = crop_source(session, CROPS[0])
    empty = tissue_crop.evaluate(base, own, TissueCrop(True, (100, 0, 0)))
    with pytest.raises(ValueError, match="outside the current surface"):
        material_bindings.resolve(own, empty, records(own))
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        material_bindings.resolve(own, own, records(own), token.handle)


def test_plain_surface_uses_canonical_topology_and_current_coordinates(session):
    base, _ = inputs(session, CASES[0])
    moved = construction.deformed(base, base.array(0) + [0.2, 0.3, -0.4])
    row = records(base)
    adapter = material_bindings.resolve(base, moved, row)
    before, after = resolved(base, row), resolved(adapter, row)
    np.testing.assert_allclose(after[[3, 7, 11]], before[[3, 7, 11]] + [0.2, 0.3, -0.4])
