"""Donor parity includes shared seam IDs, winding and curved root correspondence."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import surface_branches as branches
from anthroforge.native.curve_surfaces import Settings
from anthroforge.native.mesh import NativeCancellation
from tests.test_native_surfaces import faces, row

FIXTURE = json.loads((Path(__file__).parent / "fixtures/surfaces/branches.json").read_text())


def inputs(engine, case):
    rows = [row(engine, points) for points in case["rows"]]
    branch = branches.branch(case["boundary"], [2, 3], case["roots"])
    return rows, branch


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda v: v["name"])
def test_native_branches_match_actual_donor_vertices_and_shared_indices(session, case):
    rows, branch = inputs(session.engine, case)
    mesh = branches.geometry(session.engine, rows, 2, [branch], Settings(flip=case["flip"]))
    np.testing.assert_allclose(mesh.array(0), case["vertices"], atol=1e-10)
    assert faces(mesh) == case["faces"]


def test_branches_validate_order_overlap_closure_and_cancellation(session):
    rows, branch = inputs(session.engine, FIXTURE["cases"][0])
    engine = session.engine
    with pytest.raises(ValueError, match="ordered interior"):
        branches.geometry(engine, rows, 2, [branches.branch(0, [3, 2], [2, 1])], Settings())
    with pytest.raises(ValueError, match="distinct"):
        branches.geometry(engine, rows, 2, [branch, branch], Settings())
    cancel = NativeCancellation(engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        branches.geometry(engine, rows, 2, [branch], Settings(), cancel.handle)


def test_uniform_branch_sampling_still_shares_exact_seam_vertices(session):
    rows, branch = inputs(session.engine, FIXTURE["cases"][0])
    mesh = branches.geometry(session.engine, rows, 2, [branch], Settings(exact=False, strips=2))
    corners = faces(mesh)
    incidence = {}
    for face in corners:
        for a, b in zip(face, face[1:] + face[:1], strict=True):
            edge = tuple(sorted((a, b)))
            incidence[edge] = incidence.get(edge, 0) + 1
    assert max(incidence.values()) == 2
    assert np.isfinite(mesh.array(0)).all()
