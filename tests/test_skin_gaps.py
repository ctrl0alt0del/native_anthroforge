"""Source gap contracts ported from addon test_skin_gaps.py; no alternate gap model."""

import numpy as np
import pytest

from anthroforge.native.mesh import GeometryEngine, NativeCancellation
from anthroforge.native.skin_gaps import create


def planes(reverse=False, merged=False):
    vertices = np.array(
        [(x, y, z) for x in (0.0, 0.4) for y, z in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    )
    faces = np.array([(0, 1, 2), (0, 2, 3), (4, 5, 6), (4, 6, 7)])
    if reverse:
        faces[2:] = faces[2:, ::-1]
    owners = np.array([0, 0, 0, 0] if merged else [0, 0, 1, 1])
    policies = np.array([[0.6, 0.75, 1]] if merged else [[0.6, 0.75, 1], [0.2, 0.25, 1]])
    return vertices, faces, owners, policies


@pytest.mark.parametrize("reverse", [False, True])
def test_exact_gap_and_stricter_two_sided_settings(reverse):
    scene = create(GeometryEngine(), *planes(reverse))
    result = scene.sample([[0.2, 0, 0]], 4)[0]
    np.testing.assert_allclose(result[1:4], [0.4, 0.2, 0.25], atol=1e-14)
    assert result[4] >= 0 and result[5] >= 0
    scene.close()


def test_disjoint_patches_of_single_contributor():
    scene = create(GeometryEngine(), *planes(merged=True))
    assert scene.sample([[0.2, 0, 0]], 4)[0, 1] == pytest.approx(0.4)
    scene.close()


def test_invalid_queries_and_cancellation():
    engine = GeometryEngine()
    scene = create(engine, *planes())
    for points in ([[0, 0]], [[np.nan, 0, 0]], [0, 0, 0]):
        with pytest.raises(ValueError):
            scene.sample(points, 4)
    cancel = NativeCancellation(engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        scene.sample([[0.2, 0, 0]], 4, cancel.handle)
    scene.close()
    with pytest.raises(ValueError, match="Unknown skin"):
        scene.sample([[0.2, 0, 0]], 4)
