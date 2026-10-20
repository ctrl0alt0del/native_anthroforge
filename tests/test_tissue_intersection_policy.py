"""Accepted tissue crossings retain the original inflation and smoothing mathematics."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.tissue_settings import HeightSmoothing, TissuePart, TissueSide
from anthroforge.native import mesh_quality, tissue_inflation, tissue_parts, tissue_smoothing
from tests.test_tissue_inflation import grid_mesh, settings

CASE = json.loads(
    (Path(__file__).parent / "fixtures/tissue/control_point_crossings.json").read_text()
)


def fixture(engine):
    first, last = np.asarray(CASE["boundaries"])
    t = np.linspace(0, 1, CASE["rows"])[:, None, None]
    base = grid_mesh(engine, (1 - t) * first + t * last)
    side = TissueSide(settings(CASE["settings"]), HeightSmoothing(**CASE["smoothing"]))
    return base, (TissuePart("main", side),)


@pytest.mark.parametrize("entry", ["grid", "parts"])
def test_crossing_control_point_output_preserves_unmodified_kernel(session, entry):
    base, parts = fixture(session.engine)
    output = (
        tissue_inflation.evaluate(base, parts[0].a.inflation, CASE["reverse"])
        if entry == "grid"
        else tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    )
    for index, expected in CASE["witnesses"].items():
        np.testing.assert_allclose(output.array(0)[int(index)], expected, rtol=0, atol=1e-12)
    quality = mesh_quality.deformation(base, output)
    assert quality.new_crossings > 0 and quality.new_collapses == 0
    np.testing.assert_array_equal(base.array(3), output.array(3))


def test_smoothing_accepts_crossings_without_adding_repair(session):
    base, parts = fixture(session.engine)
    own = tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    output, reports = tissue_smoothing.evaluate(base, own, parts, "a")
    assert np.isfinite(output.array(0)).all() and reports[0].status != "NUMERICAL_FAILURE"
    assert mesh_quality.deformation(base, output).new_crossings > 0
    np.testing.assert_array_equal(output.array(3), own.array(3))
    fixed = np.linalg.norm(own.array(0) - base.array(0), axis=1) == 0
    np.testing.assert_array_equal(output.array(0)[fixed], own.array(0)[fixed])
    assert np.linalg.norm(output.array(0) - own.array(0), axis=1).max() <= 0.05 + 2e-7


def test_smoothing_off_preserves_crossing_output_exactly(session):
    base, parts = fixture(session.engine)
    own = tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    side = replace(parts[0].a, smoothing=HeightSmoothing())
    output, _ = tissue_smoothing.evaluate(base, own, (replace(parts[0], a=side),), "a")
    np.testing.assert_array_equal(output.array(0), own.array(0))
