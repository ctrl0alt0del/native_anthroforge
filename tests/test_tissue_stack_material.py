"""Stack leases preserve canonical material geometry, hidden variables and exact constraints."""

import json
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.core.tissue_constraints import TissueConstraint
from anthroforge.core.tissue_settings import TissueCrop, TissueInflation
from anthroforge.native import tissue_shapes
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.tissue_stacking import MaterialLease, assemble
from tests.stacking_material_fixtures import arrays, item, leases, ordinary
from tests.test_tissue_branches import CASES as BRANCHES
from tests.test_tissue_branches import inputs
from tests.test_tissue_crops import triangle_coordinates
from tests.test_tissue_inflation import FIXTURE, grid_mesh, settings

INFLATIONS = json.loads(FIXTURE.read_text())["cases"]


def same_geometry(output, own):
    np.testing.assert_allclose(
        triangle_coordinates(output.array(0), output.array(3)),
        triangle_coordinates(own.array(0), own.array(3)),
        atol=1e-10,
        rtol=0,
    )


@pytest.mark.parametrize("case", INFLATIONS, ids=lambda c: c["name"])
def test_material_lease_roundtrip_retains_inflation_and_world_frame(session, case):
    base = grid_mesh(session.engine, case["points"])
    config = ordinary(settings(case["settings"]), reverse=case["reverse"])
    own, first, _ = leases(base, config)
    domain = arrays(first.domain(1))
    same_geometry(assemble(first, domain["own"]), own)
    np.testing.assert_allclose(np.linalg.norm(domain["direction"], axis=1), 1, atol=1e-12)
    frame = np.eye(4)
    frame[:3, :3] = [[0, -2, 0], [0.5, 0, 0], [0, 0, 1.5]]
    frame[:3, 3] = [1, 2, 3]
    moved = MaterialLease(base, own, own, config, frame=frame.ravel())
    same_geometry(assemble(moved, arrays(moved.domain(1))["own"]), own)


@pytest.mark.parametrize("case", BRANCHES, ids=lambda c: c["name"])
@pytest.mark.parametrize("envelope", [False, True])
def test_crop_branch_and_envelope_leases_recompose_exact_material(session, case, envelope):
    base, parts = inputs(session, case)
    crop = TissueCrop(True, (0.23, 0, 0), (1, 0.2, 0))
    config = item(parts, crop=crop, both_sides=envelope)
    own, first, second = leases(base, config)
    a = arrays(first.domain(1))["own"]
    b = arrays(second.domain(2))["own"] if second else ()
    same_geometry(assemble(first, a, second, b), own)
    assert first.domain(1).material.vertices_count == base.counts[0]


def test_crop_edges_do_not_create_new_pins_and_preserve_hidden_exact_rows(session):
    base = grid_mesh(session.engine, INFLATIONS[0]["points"])
    config = ordinary(settings(INFLATIONS[0]["settings"]))
    own, first, _ = leases(base, config)
    cropped = replace(config, crop=TissueCrop(True, (0.19, 0, 0), (1, 0, 0)))
    _, cut, _ = leases(base, cropped)
    full, partial = first.domain(1).material, cut.domain(1).material
    np.testing.assert_array_equal(
        np.ctypeslib.as_array(full.fixed, (full.fixed_count,)),
        np.ctypeslib.as_array(partial.fixed, (partial.fixed_count,)),
    )
    assert partial.vertices_count == full.vertices_count and partial.samples < full.samples


def test_normal_shell_stack_changes_outer_only_and_fixed_regions_are_exact(session):
    base = grid_mesh(session.engine, INFLATIONS[0]["points"])
    config = ordinary(
        TissueInflation(mode="NORMAL", amount=0.04),
        constraints=(TissueConstraint(mask="ALL", mode="FIXED"),),
    )
    own = tissue_shapes.normal(base, config.parts[0].a.inflation)
    lease = MaterialLease(base, own, own, config)
    domain = lease.domain(1)
    assert domain.material.constraint_count == base.counts[0]
    points = arrays(domain)["own"] + [0, 0, 0.01]
    output = assemble(lease, points)
    np.testing.assert_array_equal(output.array(0)[base.counts[0] :], own.array(0)[base.counts[0] :])
    np.testing.assert_allclose(output.array(0)[: base.counts[0]], points, atol=1e-12)


def test_preparation_cancels_without_changing_intrinsic_and_rejects_lost_mapping(session):
    base = grid_mesh(session.engine, INFLATIONS[0]["points"])
    config = ordinary(settings(INFLATIONS[0]["settings"]))
    own, _, _ = leases(base, config)
    before = own.array(0).copy()
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        MaterialLease(base, own, own, config, cancel=token.handle)
    changed = replace(config, crop=TissueCrop(True, (0.123, 0, 0), (1, 0, 0)))
    with pytest.raises(ValueError, match="correspondence"):
        MaterialLease(base, own, own, changed)
    np.testing.assert_array_equal(own.array(0), before)
