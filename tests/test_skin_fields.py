"""Native field ownership, cancellation, memory bounds and numerical invariants."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.core.skin import EnvelopeSettings
from anthroforge.native.mesh import GeometryEngine, NativeCancellation
from anthroforge.native.skin_fields import prepare


def source():
    vertices = np.array([[0.0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    faces = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    return vertices, faces, np.ones(4, dtype=np.uint8), np.ones(4)


def test_fields_owned_and_collagen_endpoints():
    engine, inputs = GeometryEngine(), source()
    full = prepare(engine, *inputs, resolution=16)
    np.testing.assert_array_equal(full.array(2), 1)
    np.testing.assert_allclose(full.array(3), full.array(1), atol=1e-15)
    assert full.bytes >= np.prod(full.shape) * 32
    assert np.all(full.array(1) >= full.array(0) - 1e-15)
    full.close()
    with pytest.raises(ValueError, match="Unknown skin"):
        full.array(0)


def test_zero_collagen_core_uses_required_envelope():
    inputs = source()
    inputs[3][:] = 0
    settings = replace(EnvelopeSettings(), collagen_core_ratio=0.05, collagen_falloff_ratio=0)
    fields = prepare(GeometryEngine(), *inputs, settings=settings, resolution=24)
    mask = fields.array(2) == 0
    assert np.any(mask)
    np.testing.assert_array_equal(fields.array(3)[mask], fields.array(0)[mask])
    fields.close()


def test_memory_rejection_and_cancel_do_not_publish_fields():
    engine = GeometryEngine()
    with pytest.raises(ValueError, match="memory budget"):
        prepare(engine, *source(), resolution=16, budget=100)
    cancel = NativeCancellation(engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        prepare(engine, *source(), resolution=16, cancel=cancel.handle)


def test_source_validation_before_native_access():
    engine = GeometryEngine()
    vertices, faces, scp, weights = source()
    with pytest.raises(ValueError, match="do not match"):
        prepare(engine, vertices, faces, scp[:-1], weights, resolution=16)
    faces[0, 0] = 999
    with pytest.raises(ValueError, match="triangle index"):
        prepare(engine, vertices, faces, scp, weights, resolution=16)


def test_uniform_scale_preserves_collagen_and_scales_distance():
    inputs, engine = source(), GeometryEngine()
    first = prepare(engine, *inputs, resolution=16)
    scaled = prepare(engine, inputs[0] * 1000, *inputs[1:], resolution=16)
    np.testing.assert_allclose(first.array(2), scaled.array(2), atol=1e-12)
    for kind in (0, 1, 3):
        np.testing.assert_allclose(first.array(kind) * 1000, scaled.array(kind), atol=1e-10)
    first.close()
    scaled.close()


def test_centerline_fields_have_no_radius_or_skeletal_collagen():
    engine = GeometryEngine()
    xyz = np.array([[0.0, 0, 0], [1, 0, 0]])
    inputs = xyz, np.empty((0, 3), dtype=np.int64), np.empty(0, dtype=np.uint8), np.ones(2)
    fields = prepare(engine, *inputs, resolution=24, segments=[[0, 1]])
    assert np.isfinite(fields.array(3)).all()
    np.testing.assert_array_equal(fields.array(2), 1)
    assert fields.array(3).min() < 0 < fields.array(3).max()
    with pytest.raises(ValueError, match="segment index"):
        prepare(engine, *inputs, resolution=24, segments=[[0, 2]])
    fields.close()


def test_empty_segments_leave_surface_fields_exactly_unchanged():
    engine = GeometryEngine()
    first = prepare(engine, *source(), resolution=16)
    second = prepare(engine, *source(), resolution=16, segments=np.empty((0, 2), dtype=np.int64))
    for kind in range(4):
        np.testing.assert_array_equal(first.array(kind), second.array(kind))
    first.close()
    second.close()
