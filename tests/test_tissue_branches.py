"""Prepared branch inflation matches production geometry, seam and connector outputs."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.tissue_codec import inflation
from anthroforge.core.tissue_settings import TissuePart, TissueSide
from anthroforge.native import material, tissue_parts, topology

CASES = json.loads((Path(__file__).parent / "fixtures/tissue/branches.json").read_text())["cases"]
CORRECTED = json.loads(
    (Path(__file__).parent / "fixtures/tissue/distributed_correction.json").read_text()
)["branches"]


def inputs(session, row):
    source = base_mesh(session, row)
    source = material.restore(source, row["material"], parameters=row["axes"])
    parts = tuple(
        TissuePart(
            str(i),
            TissueSide(inflation(s)),
            connector_width=row["connectors"][2 * i],
            connector_fullness=row["connectors"][2 * i + 1],
        )
        for i, s in enumerate(row["settings"])
    )
    return source, parts


def base_mesh(session, row):
    faces = np.asarray(row["faces"])
    triangles = faces[:, ((0, 1, 2), (0, 2, 3))].reshape(-1, 3)
    arrays = [
        row["points"],
        faces.ravel(),
        np.arange(len(faces) + 1) * 4,
        triangles,
        np.repeat(np.arange(len(faces)), 2),
    ]
    return topology.restore(session.engine, arrays)


@pytest.mark.parametrize("row", CASES, ids=lambda r: r["name"])
def test_prepared_branch_correction_keeps_canonical_topology(session, row):
    source, parts = inputs(session, row)
    result = tissue_parts.evaluate(source, parts, "a", False)
    np.testing.assert_allclose(result.array(0), CORRECTED[row["name"]], atol=1e-10, rtol=0)
    np.testing.assert_array_equal(result.array(1), source.array(1))
    np.testing.assert_array_equal(result.array(3), source.array(3))
