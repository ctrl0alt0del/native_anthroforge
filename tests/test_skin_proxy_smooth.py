"""Proxy smoothing retains Blender midpoint averaging without changing anatomy."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_density, topology

DATA = json.loads((Path(__file__).parent / "fixtures/skin/proxy_smooth.json").read_text())


def mesh_from_case(engine, row):
    faces = np.asarray(row["faces"])
    triangles = faces[:, ((0, 1, 2), (0, 2, 3))].reshape(-1, 3)
    arrays = [
        row["points"],
        faces.ravel(),
        np.arange(len(faces) + 1) * 4,
        triangles,
        np.repeat(np.arange(len(faces)), 2),
    ]
    return topology.restore(engine, arrays)


@pytest.mark.parametrize("row", DATA["cases"])
def test_proxy_smooth_matches_blender_and_preserves_source(session, row):
    mesh = mesh_from_case(session.engine, row)
    before = mesh.array(0).copy()
    result = skin_density.smooth_proxy(mesh, iterations=row["iterations"])
    np.testing.assert_allclose(result.array(0), row["result"], atol=3e-7, rtol=0)
    np.testing.assert_array_equal(mesh.array(0), before)
    np.testing.assert_array_equal(result.array(1), mesh.array(1))


def test_disabled_smoothing_does_not_round_original_coordinates(session):
    mesh = mesh_from_case(session.engine, DATA["cases"][0])
    result = skin_density.smooth_proxy(mesh, factor=0)
    np.testing.assert_array_equal(result.array(0), mesh.array(0))
