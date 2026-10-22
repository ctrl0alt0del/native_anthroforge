"""Material clipping retains donor shapes and exact source interpolation after cropping."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.assets import Asset
from anthroforge.core.tissue_settings import TissueCrop, TissueInflation
from anthroforge.native import (
    construction,
    tissue_crop,
    tissue_domain,
    tissue_inflation,
    tissue_parts,
    topology,
)
from tests.test_tissue_branches import CASES as BRANCHES
from tests.test_tissue_branches import inputs as branch_inputs
from tests.test_tissue_envelopes import CASES as ENVELOPES
from tests.test_tissue_inflation import grid_mesh
from tests.test_tissue_smoothing import CASES as SOURCES
from tests.test_tissue_smoothing import inputs

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/crops.json").read_text())["cases"]


def source(session, row):
    if "source" in row:
        base, own, _ = inputs(session, SOURCES[row["source"]])
        return base, own
    envelope = ENVELOPES[row["envelope"]]
    base, parts = branch_inputs(session, BRANCHES[envelope["source"]])
    prototype = tissue_parts.evaluate(base, parts, "a", False)
    first = construction.deformed(prototype, envelope["first"])
    second = construction.deformed(prototype, envelope["second"])
    return base, tissue_parts.compose(first, second, False)


def triangle_coordinates(vertices, faces):
    rows = []
    for face in faces:
        values = np.asarray(vertices)[face]
        order = np.lexsort(values.T[::-1])
        rows.append(values[order].ravel())
    rows = np.asarray(rows).reshape(-1, 9)
    return rows[np.lexsort(rows.T[::-1])]


@pytest.mark.parametrize("row", CASES)
def test_crop_matches_addon_material_shape_including_composed_sides(session, row):
    base, own = source(session, row)
    result = tissue_crop.evaluate(base, own, TissueCrop(enabled=True, **row["plane"]))
    expected = triangle_coordinates(row["vertices"], row["faces"])
    observed = triangle_coordinates(result.array(0), result.array(3))
    np.testing.assert_allclose(observed, expected, atol=1e-10, rtol=0)
    if "source" in row:
        np.testing.assert_allclose(
            result.array(0), np.asarray(row["vertices"]).reshape(-1, 3), atol=1e-10
        )
        np.testing.assert_array_equal(result.array(1), np.asarray(row["faces"]).ravel())


def material_positions(base, output):
    records, weights = tissue_domain.arrays(output)
    n, entries = records[5], records[7]
    offsets, indices = records[8 : 9 + n], records[9 + n : 9 + n + entries]
    return np.array(
        [
            sum(
                (weights[k] * base.array(0)[indices[k]] for k in range(offsets[i], offsets[i + 1])),
                start=np.zeros(3),
            )
            for i in range(n)
        ]
    ).reshape(-1, 3)


def test_crop_edges_retain_nonzero_height_and_paired_material_coordinates(session):
    row = CASES[0]
    base, own = source(session, row)
    result = tissue_crop.evaluate(base, own, TissueCrop(enabled=True, **row["plane"]))
    material = material_positions(base, result)
    np.testing.assert_allclose(material, row["base"], atol=1e-12)
    distances = (material - np.asarray(row["plane"]["origin"])) @ row["plane"]["normal"]
    heights = np.linalg.norm(result.array(0) - material, axis=1)
    assert np.max(heights[np.abs(distances) < 1e-10]) > 0.005


def test_empty_output_is_finalized_and_safe_for_picking_and_drafts(session):
    base, own = source(session, CASES[2])
    empty = tissue_crop.evaluate(base, own, TissueCrop(enabled=True, **CASES[2]["plane"]))
    assert empty.prepared and not empty.counts[4]
    assert session.engine.pick(empty, np.eye(4).ravel(), [0, 0, 1], [0, 0, -1]) is None
    assert Asset(empty, "crop", "", 1, False).mesh is empty
    with pytest.raises(ValueError, match="finalized"):
        Asset(topology.draft(empty, 0), "draft", "", 1, False)


def test_crop_uses_material_projection_instead_of_display_quad_diagonal(session):
    base = grid_mesh(session.engine, [[[0, 0, 0], [0, 1, 3]], [[1, 0, 3], [1, 1, 0]]])
    base = topology.finalize_surface(base, None, 0)
    own = tissue_inflation.evaluate(base, TissueInflation(enabled=False))
    np.testing.assert_array_equal(base.array(3), [[0, 2, 1], [2, 3, 1]])
    crop = TissueCrop(enabled=True, origin=(0, 0, -1), normal=(0, 0, 1))
    output = tissue_crop.evaluate(base, own, crop)
    np.testing.assert_array_equal(output.array(3), [[0, 2, 3], [0, 3, 1]])
    np.testing.assert_array_equal(material_positions(base, output), base.array(0))
