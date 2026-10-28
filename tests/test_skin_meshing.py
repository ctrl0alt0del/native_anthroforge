"""Exact MC33 qualification against the addon's compiled scikit-image backend."""

import numpy as np
import pytest

from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.skin_fields import tile_mesh


def compare(engine, volume):
    measure = pytest.importorskip("skimage.measure")
    expected, faces, _, _ = measure.marching_cubes(volume, 0, allow_degenerate=False)
    actual = tile_mesh(engine, volume)
    np.testing.assert_array_equal(actual.array(0), expected)
    np.testing.assert_array_equal(actual.array(1).reshape(-1, 3), faces)


def test_every_binary_cube_case():
    engine = GeometryEngine()
    for bits in range(1, 255):
        volume = np.array([1.0 if (bits >> i) & 1 else -1.0 for i in range(8)], np.float32)
        compare(engine, volume.reshape(2, 2, 2))


def test_zero_corner_degeneracies():
    engine = GeometryEngine()
    for case in range(3**8):
        volume = np.array([(case // (3**i)) % 3 - 1 for i in range(8)], np.float32)
        if volume.min() < 0 < volume.max():
            compare(engine, volume.reshape(2, 2, 2))


@pytest.mark.parametrize("size", [4, 9, 33])
def test_random_tiles_preserve_connectivity(size):
    engine, random = GeometryEngine(), np.random.default_rng(42)
    for _ in range(4):
        compare(engine, random.uniform(-1, 1, (size, size, size)).astype(np.float32))


def test_invalid_tile_is_rejected():
    engine = GeometryEngine()
    for value in (np.zeros((34, 2, 2)), np.full((2, 2, 2), np.nan)):
        with pytest.raises(ValueError):
            tile_mesh(engine, value)
