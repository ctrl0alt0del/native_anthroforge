"""Captured production addon results, including exact/feathered regions and convergence."""

import json
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from anthroforge.core.tissue_constraints import TissueConstraint, TissueField
from anthroforge.core.tissue_settings import (
    TissueInflation,
    TissuePart,
    TissueRelaxation,
    TissueSide,
)
from anthroforge.native import paths, tissue_relaxation
from tests.test_tissue_shapes import shell, sweep

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/relaxation.json").read_text())["cases"]


def definition(row):
    s = row["settings"]
    inflation = TissueInflation(mode=row["source"]["kind"], amount=0.12, minimum=0.006, power=0.8)
    return NS(
        relaxation=relaxation(s),
        parts=(TissuePart(a=TissueSide(inflation)),),
        constraints=tuple(constraint(r) for r in s["attachments"]),
        fields=tuple(TissueField(k, tuple(v)) for k, v in row["fields"].items()),
    )


def relaxation(s):
    return TissueRelaxation(
        s["relaxation_mode"],
        tuple(s["gravity"]),
        s["sagginess"],
        s["sag_limit"],
        s["shape_retention"],
        s["volume_retention"],
        s["surface_slack"],
        s["iterations"],
        s["constraint_passes"],
        s["tolerance"],
    )


def constraint(row):
    return TissueConstraint(
        mode=row["mode"],
        mask=row["mask_attribute"],
        strength=row["strength"],
        feather=row["feather"],
        offset=row["normal_offset"],
    )


def source(session, row):
    value = tissue_relaxation.Source()
    value.frame[:] = np.eye(4).ravel()
    if row["kind"] == "NORMAL":
        faces = row["faces"]
        lease = session.engine.create_mesh(
            row["points"], np.array(faces).ravel(), np.arange(len(faces) + 1) * 4
        )
        value.mesh = lease.handle
    else:
        samples = np.zeros((len(row["points"]), 11))
        samples[:, :3], samples[:, 6:9], samples[:, 3] = row["points"], row["normals"], 1
        lease = paths.restore(session.engine, samples, np.linspace(0, 1, len(samples)), False)
        value.path = lease.handle
    return value, lease


@pytest.mark.parametrize("row", CASES)
def test_relaxation_matches_addon_source_regions_and_diagnostics(session, row):
    shape = row["source"]
    rest = shell(session, shape) if shape["kind"] == "NORMAL" else sweep(session, shape)
    input_source, lease = source(session, shape)
    output, diagnostic = tissue_relaxation.evaluate(rest, input_source, definition(row))
    np.testing.assert_allclose(rest.array(0), row["rest"], atol=1e-12, rtol=0)
    expected = (
        row["owned_output"] if row["settings"]["relaxation_mode"] == "STATIC_PBD" else row["output"]
    )
    tolerance = 1e-10 if row["settings"]["relaxation_mode"] == "STATIC_PBD" else 2e-7
    np.testing.assert_allclose(output.array(0), expected, atol=tolerance, rtol=0)
    if row["settings"]["relaxation_mode"] == "STATIC_PBD":
        assert diagnostic.status == row["report"]["status"]
        assert diagnostic.iterations == row["report"]["iterations"]
    assert lease.handle and diagnostic.max_fixed_error == 0


@pytest.mark.parametrize("row", CASES[3:6])
def test_double_precision_source_goals_bound_difference_from_blender_capture(session, row):
    rest = shell(session, row["source"])
    input_source, lease = source(session, row["source"])
    output, _ = tissue_relaxation.evaluate(rest, input_source, definition(row))
    assert lease.handle
    # Legacy mathutils goal rounding is amplified by the iterative envelope solve.
    # The separate exact-input comparison above isolates the port from that perturbation.
    np.testing.assert_allclose(output.array(0), row["output"], atol=2e-5, rtol=0)
