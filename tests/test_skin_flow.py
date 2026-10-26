"""Native cross-field parity inputs and cancellation safeguards."""

import numpy as np
import pytest

from anthroforge.native import skin_flow
from anthroforge.native.mesh import NativeCancellation


def fixture(engine, angle=0.4):
    vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    mesh = engine.create_mesh(vertices, [0, 1, 2, 0, 2, 3], [0, 3, 6])
    centers = mesh.array(0)[mesh.array(3)].mean(axis=1)
    prior = np.tile([1.0, 0.0, 0.0], (2, 1))
    directions = np.tile([np.cos(angle), np.sin(angle), 0], (2, 1))
    samples = np.column_stack((centers, directions, np.tile([0, 0, 1], (2, 1)), [0, 1]))
    return mesh, prior, samples


def test_guidance_changes_field_without_mutating_mesh(session):
    mesh, prior, samples = fixture(session.engine)
    before = mesh.array(0).copy()
    output, information = skin_flow.solve(mesh, prior, samples)
    np.testing.assert_allclose(np.linalg.norm(output, axis=1), 1, atol=1e-12)
    np.testing.assert_array_equal(mesh.array(0), before)
    assert np.all(information[:, 0] > 0)
    assert np.linalg.norm(output - prior) > 0.1


def test_empty_guidance_uses_transported_prior(session):
    mesh, prior, _ = fixture(session.engine)
    output, information = skin_flow.solve(mesh, prior, np.empty((0, 10)))
    assert np.isfinite(output).all()
    np.testing.assert_array_equal(information[:, 0], 0)


def test_invalid_samples_and_cancel_are_explicit(session):
    mesh, prior, samples = fixture(session.engine)
    broken = samples.copy()
    broken[0, 3] = np.nan
    with pytest.raises(ValueError, match="Nonfinite"):
        skin_flow.solve(mesh, prior, broken)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_flow.solve(mesh, prior, samples, cancel.handle)
