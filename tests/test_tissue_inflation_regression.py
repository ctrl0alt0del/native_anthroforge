"""Saved bent membrane: valid inflation, exact boundaries and stable refinement."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.tissue_settings import (
    HeightSmoothing,
    TissueInflation,
    TissuePart,
    TissueSide,
)
from anthroforge.native import (
    construction,
    material,
    mesh_quality,
    tissue_inflation,
    tissue_parts,
    tissue_smoothing,
)
from tests.test_tissue_inflation import grid_mesh

CASE = json.loads((Path(__file__).parent / "fixtures/tissue/bent_membrane.json").read_text())


def bent_base(engine):
    first, last = np.asarray(CASE["boundaries"])
    t = np.linspace(0, 1, CASE["rows"])[:, None, None]
    base = grid_mesh(engine, (1 - t) * first + t * last)
    parameters = CASE["axes"] or [
        i / (count - 1) for count in (CASE["rows"], len(first)) for i in range(count)
    ]
    return material.restore(base, material.array(base), parameters=parameters)


def settings(amount):
    inflation = TissueInflation(mode="DISTRIBUTED", amount=amount, boundary_band=0.1)
    return (TissuePart("main", TissueSide(inflation, HeightSmoothing("HEIGHT", 0.2, 0.8, 0.05))),)


def valid(before, after):
    quality = mesh_quality.deformation(before, after)
    assert quality.baseline_crossings == quality.new_crossings == quality.new_collapses == 0


@pytest.mark.parametrize("amount", [0.02, 0.1, 1.0])
def test_saved_bend_inflates_and_smooths_without_crossings(session, amount):
    source = bent_base(session.engine)
    base = tissue_inflation.refine(source, 24)
    parts = settings(amount)
    own = tissue_parts.evaluate(base, parts, "a", True)
    output, reports = tissue_smoothing.evaluate(base, own, parts, "a")
    valid(base, own)
    valid(base, output)
    np.testing.assert_array_equal(output.array(3), base.array(3))
    fixed = np.linalg.norm(own.array(0) - base.array(0), axis=1) == 0
    np.testing.assert_array_equal(output.array(0)[fixed], base.array(0)[fixed])
    assert np.linalg.norm(output.array(0) - own.array(0), axis=1).max() <= 0.05 + 2e-7
    assert reports[0].stationarity <= 2e-7


def test_refinement_preserves_dense_source_and_does_not_insert_slivers(session):
    source = bent_base(session.engine)
    refined = tissue_inflation.refine(source, 24)
    np.testing.assert_allclose(refined.array(0), source.array(0), atol=1e-15, rtol=0)
    np.testing.assert_array_equal(material.axes(refined), material.axes(source))
    dense = tissue_inflation.refine(source, 128)
    for old, new in zip(axes(source), axes(dense), strict=True):
        assert all(np.any(new == t) for t in old)
        assert np.diff(new).max() <= 1 / 127 + 1e-12
        assert np.diff(new).min() >= min(np.diff(old).min(), 1 / 254) - 1e-12


def axes(mesh):
    rows = material.array(mesh)[0]
    values = material.axes(mesh)
    return values[:rows], values[rows:]


def test_distributed_directions_are_rigid_and_scale_equivariant(session):
    source = bent_base(session.engine)
    config = settings(0.1)[0].a.inflation
    output = tissue_inflation.evaluate(source, config, True)
    rotation = np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]])
    moved = construction.deformed(source, 3 * source.array(0) @ rotation + [2, 3, 4])
    result = tissue_inflation.evaluate(moved, replace(config, amount=0.3), True)
    np.testing.assert_allclose(
        result.array(0), 3 * output.array(0) @ rotation + [2, 3, 4], atol=1e-9
    )


def test_planar_distributed_preserves_authored_height_and_boundary(session):
    y, x = np.mgrid[0:7, 0:9]
    base = grid_mesh(session.engine, np.stack((x / 8, y / 6, x * 0), axis=-1))
    config = TissueInflation(mode="DISTRIBUTED", amount=1, boundary_band=0.1)
    mesh = tissue_inflation.evaluate(base, config, True)
    output = mesh.array(0).reshape(7, 9, 3)
    np.testing.assert_allclose(output[1:-1, 1:-1, 2], 1, atol=1e-12)
    np.testing.assert_allclose(
        output[:, :, :2], base.array(0).reshape(7, 9, 3)[:, :, :2], atol=1e-12
    )
    np.testing.assert_array_equal(output[[0, -1], :, 2], 0)
    np.testing.assert_array_equal(output[:, [0, -1], 2], 0)
