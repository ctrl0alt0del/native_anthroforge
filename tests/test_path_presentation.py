"""Owned render chunks and cached transformed picking follow exact path geometry."""

import ctypes as c
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application.primitive_operations import straight_curve
from anthroforge.core.construction import CurvePoint
from anthroforge.core.curve_engines import decode
from anthroforge.core.entities import IDENTITY
from anthroforge.native import paths
from anthroforge.native.mesh import U
from tests.test_native_paths import triangle


def chunk(path, index):
    output, count = c.POINTER(c.c_float)(), c.c_int()
    path.engine.bind(
        "af_path_chunk", [U, c.c_int, c.POINTER(c.POINTER(c.c_float)), c.POINTER(c.c_int)]
    )
    path.engine.check(
        path.engine.library.af_path_chunk(path.handle, index, c.byref(output), c.byref(count))
    )
    return np.ctypeslib.as_array(output, shape=(count.value,)).reshape((-1, 3)).copy()


def test_closed_render_path_has_closing_edge_without_adding_authored_sample(session):
    path = paths.evaluate(session.engine, replace(triangle(), engine_settings=decode("POLYLINE")))
    rendered = chunk(path, 0)
    assert path.count == 3 and len(rendered) == 4
    np.testing.assert_array_equal(rendered[0], rendered[-1])
    np.testing.assert_allclose(rendered[:3], path.array()[:, :3])


def test_long_path_uses_bounded_chunks_with_shared_seams(session):
    points = tuple(CurvePoint(position=(i * 0.01, 0, 0)) for i in range(5000))
    path = paths.evaluate(
        session.engine, replace(straight_curve(), points=points, engine_settings=decode("POLYLINE"))
    )
    chunks = [chunk(path, i) for i in range(path.chunks)]
    assert path.chunks == 3 and max(map(len, chunks)) <= 2049
    for first, second in zip(chunks, chunks[1:], strict=False):
        np.testing.assert_array_equal(first[-1], second[0])
    stitched = np.concatenate([chunks[0], *(part[1:] for part in chunks[1:])])
    np.testing.assert_allclose(stitched, path.array()[:, :3], atol=2e-6)
    assert path.bytes > path.array().nbytes + stitched.nbytes


@pytest.mark.parametrize("scales", [(1, 1, 1), (-2, 0.25, 3)])
def test_cached_path_picking_uses_world_distance_under_nonuniform_transforms(session, scales):
    path = paths.evaluate(
        session.engine, replace(straight_curve(), engine_settings=decode("POLYLINE"))
    )
    matrix = session.engine.transform([1, 2, 0, 0, 0, 37, *scales])
    hits = paths.pick(session.engine, [path.handle], [matrix], [1, 2, 4], [0, 0, -2], 0.01)
    assert hits.shape == (1, 6) and hits[0, 1] == pytest.approx(4)
    assert not len(paths.pick(session.engine, [path.handle], [matrix], [1, 2, 4], [0, 0, 1], 0.01))
    np.testing.assert_allclose(hits[0, 3:], [1, 2, 0])


def test_closed_path_final_edge_is_pickable_and_empty_batch_is_valid(session):
    path = paths.evaluate(session.engine, replace(triangle(), engine_settings=decode("POLYLINE")))
    center = (path.array()[0, :3] + path.array()[-1, :3]) * 0.5
    hits = paths.pick(
        session.engine, [path.handle], [IDENTITY], center + [0, 0, 2], [0, 0, -1], 0.01
    )
    assert hits[0, 2] == 2
    assert paths.pick(session.engine, [], [], [0, 0, 1], [0, 0, -1], 0.1).shape == (0, 6)


def test_invalid_path_query_reports_error_without_undefined_buffers(session):
    path = paths.evaluate(session.engine, straight_curve())
    with pytest.raises(ValueError, match="Invalid"):
        paths.pick(session.engine, [path.handle], [IDENTITY], [0, 0, 1], [0, 0, 0], 0.1)
    with pytest.raises(ValueError, match="one transform"):
        paths.pick(session.engine, [path.handle], [], [0, 0, 1], [0, 0, -1], 0.1)
