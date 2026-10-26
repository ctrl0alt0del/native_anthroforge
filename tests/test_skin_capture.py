"""Native scene packing preserves source identity, world shape and reflected orientation."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native.mesh import GeometryEngine, NativeCancellation
from anthroforge.native.skin_capture import capture


def triangle(engine):
    return engine.create_mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [0, 1, 2], [0, 3])


def test_capture_transforms_reflections_and_keeps_source_local_order():
    engine = GeometryEngine()
    mesh = triangle(engine)
    reflected = np.eye(4)
    reflected[0, 0], reflected[0, 3] = -2, 4
    value = capture(engine, [mesh, mesh], [IDENTITY, reflected.ravel()], [[0.1, 1, 1], [0, 0, 0]])
    np.testing.assert_array_equal(value.vertices[3:], [[4, 0, 0], [2, 0, 0], [4, 1, 0]])
    np.testing.assert_array_equal(value.triangles, [[0, 1, 2], [5, 4, 3]])
    np.testing.assert_array_equal(value.owners, [0, 1])
    np.testing.assert_array_equal(value.skeletal, [1, 0])
    np.testing.assert_allclose(value.policies, [[0.4, 1, 1], [0, 0, 0]])
    np.testing.assert_array_equal(mesh.array(0), [[0, 0, 0], [1, 0, 0], [0, 1, 0]])


def test_capture_rejects_invalid_frames_and_policies():
    engine = GeometryEngine()
    mesh = triangle(engine)
    with pytest.raises(ValueError, match="transform"):
        capture(engine, [mesh], [np.zeros(16)], [[0, 1, 1]])
    with pytest.raises(ValueError, match="policy"):
        capture(engine, [mesh], [IDENTITY], [[float("nan"), 1, 1]])
    with pytest.raises(ValueError, match="per source"):
        capture(engine, [mesh], [], [])


def test_capture_respects_existing_cancellation_token():
    engine = GeometryEngine()
    mesh = triangle(engine)
    token = NativeCancellation(engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        capture(engine, [mesh], [IDENTITY], [[0, 1, 1]], token.handle)
