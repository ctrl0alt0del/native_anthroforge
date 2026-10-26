"""Parity for the Blender geometry-only subset on skin's canonical triangle inputs."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_proxy
from tools.check_skin_decimation import mesh

FIXTURES = Path(__file__).parent / "fixtures/skin"
CASES = [
    row
    for name in ("bmesh_decimation", "bmesh_normals")
    for row in json.loads((FIXTURES / (name + ".json")).read_text())["cases"]
]


@pytest.mark.parametrize("row", CASES, ids=lambda row: row["name"])
def test_blender_collapse_preserves_vertices_and_connectivity(session, row):
    points, faces = np.array(row["source"]["points"]), np.array(row["source"]["faces"])
    source = mesh(session.engine, points, faces)
    result = skin_proxy.decimate(source, row["target"])
    np.testing.assert_array_equal(result.array(0), row["result"]["points"])
    np.testing.assert_array_equal(result.array(3), row["result"]["faces"])
    np.testing.assert_array_equal(source.array(0), points)
    np.testing.assert_array_equal(source.array(3), faces)
