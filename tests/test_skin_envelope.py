"""Native assembled envelope ownership, cancellation and source-controlled geometry."""

from concurrent.futures import ThreadPoolExecutor
from time import monotonic, sleep

import numpy as np
import pytest

from anthroforge.native.mesh import GeometryEngine, NativeCancellation
from anthroforge.native.skin_fields import prepare
from anthroforge.native.skin_gaps import create

CUBE_VERTICES = np.array(
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
    dtype=float,
)
CUBE_FACES = np.array(
    [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (1, 2, 6),
        (1, 6, 5),
        (2, 3, 7),
        (2, 7, 6),
        (3, 0, 4),
        (3, 4, 7),
    ]
)


def cube():
    return CUBE_VERTICES.copy(), CUBE_FACES.copy()


def prepared(resolution=24):
    engine = GeometryEngine()
    vertices, faces = cube()
    fields = prepare(engine, vertices, faces, np.ones(12), np.ones(8), resolution=resolution)
    scene = create(engine, vertices, faces, np.zeros(12), [[0.005, 1.0, 1.0]])
    return engine, fields, scene


def test_cube_matches_source_control_counts_and_is_prepared():
    _engine, fields, scene = prepared()
    mesh = scene.envelope(fields)
    assert mesh.prepared
    assert mesh.array(0).shape == (11703, 3)
    assert mesh.array(1).size == 23180 * 3
    assert np.isfinite(mesh.array(0)).all()
    again = scene.envelope(fields)
    np.testing.assert_array_equal(mesh.array(0), again.array(0))
    np.testing.assert_array_equal(mesh.array(1), again.array(1))


def wait_for_tiles(scene, future):
    deadline = monotonic() + 10
    while scene.progress()[0] < 1 and not future.done() and monotonic() < deadline:
        sleep(0.001)
    assert scene.progress()[0] >= 1 and not future.done()


def test_running_tiles_cancel_without_poisoning_scene():
    engine, fields, scene = prepared(64)
    cancel = NativeCancellation(engine)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(scene.envelope, fields, 1024**3, cancel.handle)
        wait_for_tiles(scene, future)
        cancel.set()
        with pytest.raises(ValueError, match="[Cc]ancel"):
            future.result(timeout=10)
    assert scene.sample([[2.0, 0, 0]], 4).shape == (1, 13)
    assert scene.envelope(fields).prepared


def test_budget_failure_preserves_fields_and_source_queries():
    _engine, fields, scene = prepared()
    before = fields.array(3)
    with pytest.raises(ValueError, match="memory budget"):
        scene.envelope(fields, budget=100)
    np.testing.assert_array_equal(fields.array(3), before)
    assert scene.envelope(fields).prepared
