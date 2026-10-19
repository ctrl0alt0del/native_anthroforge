"""Height solver parity and hard material constraints, independent of inflation timing."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.tissue_settings import HeightSmoothing, TissuePart, TissueSide
from anthroforge.native import construction, material, tissue_domain, tissue_parts, tissue_smoothing
from anthroforge.native.mesh import NativeCancellation
from tests.test_tissue_branches import base_mesh

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/smoothing.json").read_text())["cases"]


def inputs(session, row):
    base = material.restore(
        base_mesh(session, row), row["material"], parameters=row.get("axes", ())
    )
    settings = HeightSmoothing("HEIGHT", 0.2, 0.8, 0.03)
    parts = tuple(TissuePart(str(i), TissueSide(smoothing=settings)) for i in range(row["count"]))
    own = construction.deformed(tissue_parts.evaluate(base, parts, "a", False), row["output"])
    return base, own, parts


@pytest.mark.parametrize("row", CASES, ids=lambda r: r["name"])
def test_height_output_matches_addon_and_preserves_correspondence(session, row):
    base, own, parts = inputs(session, row)
    result, reports = tissue_smoothing.evaluate(base, own, parts, "a")
    np.testing.assert_allclose(result.array(0), row["expected"], atol=1e-10, rtol=0)
    np.testing.assert_array_equal(result.array(3), own.array(3))
    np.testing.assert_array_equal(tissue_domain.arrays(result)[0], tissue_domain.arrays(own)[0])
    for report, expected in zip(reports, row["reports"], strict=True):
        assert report.samples == expected["samples"] and report.pinned == expected["pinned"]
        assert report.violation <= 2e-7 and report.stationarity <= 2e-7
        assert report.max_displacement <= 0.03 + 2e-7


def test_off_bypasses_native_call_and_cancellation_does_not_mutate_input(session):
    base, own, parts = inputs(session, CASES[0])
    off = tuple(replace(p, a=replace(p.a, smoothing=HeightSmoothing())) for p in parts)
    result, reports = tissue_smoothing.evaluate(base, own, off, "a")
    assert result is own and not reports
    before = own.array(0).copy()
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        tissue_smoothing.evaluate(base, own, parts, "a", token.handle)
    np.testing.assert_array_equal(own.array(0), before)


def test_zero_height_crease_and_boundary_remain_exact(session):
    base, own, parts = inputs(session, CASES[0])
    values = own.array(0).copy()
    values[25:30] = base.array(0)[25:30]
    own = construction.deformed(own, values)
    result, _ = tissue_smoothing.evaluate(base, own, parts, "a")
    zero = np.linalg.norm(values - base.array(0), axis=1) == 0
    np.testing.assert_array_equal(result.array(0)[zero], values[zero])
