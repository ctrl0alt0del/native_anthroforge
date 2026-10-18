"""Owned path buffers, native engine parity and array lifetime guarantees."""

import gc
import weakref
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application.primitive_operations import straight_curve
from anthroforge.core.construction import CurvePoint, ResolvedPrimitive
from anthroforge.native import bodies, construction, paths
from anthroforge.native.mesh import NativeCancellation


def triangle():
    source = straight_curve()
    return replace(source, points=(*source.points, CurvePoint(position=(0, 1, 0))), closed=True)


def test_native_bezier_path_preserves_existing_open_curve_evaluation(session):
    curve = straight_curve()
    path = paths.evaluate(session.engine, curve)
    expected = bodies.path(session.engine, curve, 0)
    np.testing.assert_array_equal(path.array(), expected)
    assert path.count == len(expected) and not path.closed
    assert path.bytes >= path.array().nbytes


def test_polyline_is_exact_not_fitted_or_resampled(session):
    curve = replace(triangle(), engine="POLYLINE", closed=False)
    path = paths.evaluate(session.engine, curve)
    np.testing.assert_array_equal(path.array()[:, :3], [p.position for p in curve.points])
    np.testing.assert_array_equal(path.array(1), [0, 1, 2])
    assert path.count == 3


@pytest.mark.parametrize("engine", ["BEZIER", "POLYLINE"])
def test_closed_paths_keep_authored_start_and_omit_duplicate_endpoint(session, engine):
    curve = replace(triangle(), engine=engine)
    path = paths.evaluate(session.engine, curve)
    np.testing.assert_array_equal(path.array()[0, :3], curve.points[0].position)
    assert not np.array_equal(path.array()[0, :3], path.array()[-1, :3])
    assert path.closed and path.count >= 3
    assert np.isfinite(path.array()).all()


def test_path_arrays_are_readonly_and_retain_native_allocation(session):
    path = paths.evaluate(session.engine, straight_curve())
    reference = weakref.ref(path)
    samples = path.array()
    before = samples.copy()
    del path
    gc.collect()
    assert reference() is not None
    with pytest.raises(ValueError, match="read-only"):
        samples[0, 0] = 99
    np.testing.assert_array_equal(samples, before)
    del samples
    gc.collect()
    assert reference() is None


def test_path_restore_preserves_samples_parameters_and_bounds(session):
    source = paths.evaluate(session.engine, triangle())
    restored = paths.restore(session.engine, source.array(), source.array(1), source.closed)
    np.testing.assert_array_equal(restored.array(), source.array())
    np.testing.assert_array_equal(restored.array(1), source.array(1))
    assert restored.bounds == source.bounds
    assert restored.handle != source.handle


def test_native_path_evaluation_obeys_cancellation(session):
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancelled"):
        paths.evaluate(session.engine, straight_curve(), cancel.handle)


def test_zero_length_path_does_not_publish_nan_frames(session):
    point = CurvePoint(position=(0, 0, 0))
    curve = replace(
        straight_curve(), points=(point, replace(point, id="second")), engine="POLYLINE"
    )
    with pytest.raises(ValueError, match="zero length|degenerate"):
        paths.evaluate(session.engine, curve)


@pytest.mark.parametrize("closed", [False, True])
def test_accepted_path_body_preserves_existing_blender_curve_modifier_samples(session, closed):
    curve = replace(triangle(), closed=closed)
    path = paths.evaluate(session.engine, curve)
    samples = paths.body(path, len(curve.points) - 1 if closed else 0)
    np.testing.assert_allclose(samples, bodies.path(session.engine, curve, 0), atol=1e-12)


@pytest.mark.parametrize("closed", [False, True])
def test_accepted_path_loft_matches_existing_sampling_ranges_and_transform(session, closed):
    matrix = session.engine.transform([0.5, 0.2, 0.3, 12, 18, 24, 1, 2, 3])
    curve = replace(triangle(), closed=closed, matrix=matrix)
    definition = ResolvedPrimitive(
        "LOFT", curves=(curve, replace(curve, id="other")), samples=64, start=0.1, span=0.8
    )
    path = paths.evaluate(session.engine, curve)
    samples = paths.sample(path, 64, 0.1, 0.8, matrix)
    np.testing.assert_allclose(
        samples, construction.sample_curve(session.engine, curve, definition), atol=1e-12
    )
