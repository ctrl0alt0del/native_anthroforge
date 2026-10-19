"""Dense field deformation, retained controls and buffer contracts."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.entities import IDENTITY
from anthroforge.native import attachment_fields as fields
from anthroforge.native import construction, paths
from anthroforge.native.mesh import NativeCancellation


def capture(session):
    engine = session.engine
    mesh = engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)
    curve = Curve(tuple(CurvePoint(position=(x, 0, 0.7)) for x in (0, 0.75, 1.5)))
    path = paths.evaluate(engine, curve)
    frames = [IDENTITY, engine.transform([1.5, 0, 0, 0, 0, 0, 1, 1, 1])]
    spec = fields.Capture(
        path, construction.resolved_curve(engine, curve), IDENTITY, [0, 2], [0, 1]
    )
    surfaces = ([mesh.handle, mesh.handle], frames)
    field = fields.capture(engine, surfaces, spec)
    return mesh, surfaces, field


def test_dense_displacements_match_retained_owner_weights(session):
    mesh, surfaces, field = capture(session)
    moved = [surfaces[1][0], session.engine.transform([1.5, 0, 1, 0, 0, 0, 1, 1, 1])]
    result, controls = fields.resolve(session.engine, (surfaces[0], moved), field, IDENTITY)
    weights = np.where(field.owners == 1, field.weights, 0).sum(axis=1)
    expected = field.path.array()[:, :3].copy()
    expected[:, 2] += weights[: field.path.count]
    np.testing.assert_allclose(result.array()[:, :3], expected, atol=1e-12)
    np.testing.assert_allclose(controls[:, 2], field.records[:, 2] + weights[field.path.count :: 3])
    assert result.count == field.path.count and np.any((weights > 0) & (weights < 1))
    np.testing.assert_array_equal(result.array(1), field.path.array(1))


def test_native_cancel_retains_immutable_capture(session):
    mesh, surfaces, field = capture(session)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        fields.resolve(session.engine, surfaces, field, IDENTITY, cancel.handle)
    for array in (field.owners, field.weights, field.bindings, field.records):
        assert not array.flags.writeable
    path, _ = fields.resolve(session.engine, surfaces, field, IDENTITY)
    np.testing.assert_allclose(path.array()[:, :3], field.path.array()[:, :3], atol=1e-12)


def test_malformed_buffer_dtype_rejected_before_native_access(session):
    mesh, surfaces, field = capture(session)
    with pytest.raises(ValueError, match="typed data"):
        replace(field, owners=field.owners.astype(np.float64))
    with pytest.raises(ValueError, match="record layout"):
        replace(field, bindings=field.bindings[:, :, :27].copy())
