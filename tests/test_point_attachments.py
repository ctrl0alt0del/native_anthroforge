"""Point attachments reuse canonical surface coordinates without synthetic document objects."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import point_attachments as binding
from anthroforge.native.mesh import NativeCancellation


@pytest.fixture
def cube(session):
    return session.engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)


def test_capture_resolves_exact_off_surface_points_under_affine_transforms(session, cube):
    frame = session.engine.transform([0.2, 0.4, -0.1, 17, 23, -11, -2, 0.3, 1.5])
    points = [[-1, 0.8, 0.7], [0.1, -0.6, 0.2], [0.5, 0.3, 1]]
    targets, records = binding.capture(session.engine, [cube.handle], [frame], points)
    output = binding.resolve(session.engine, [cube.handle], [frame], targets, records)
    np.testing.assert_allclose(output[:, [3, 7, 11]], points, atol=1e-12)
    assert not session.document.objects and not session.document.entities
    assert np.all(records[:, :3] >= 0)


def test_nearest_candidates_can_be_overridden_and_do_not_switch_during_resolution(session, cube):
    translated = session.engine.transform([2, 0, 0, 0, 0, 0, 1, 1, 1])
    meshes, frames = [cube.handle, cube.handle], [IDENTITY, translated]
    targets, records = binding.capture(
        session.engine, meshes, frames, [[0, 0, 0.8], [2, 0, 0.8]], [-1, 0]
    )
    np.testing.assert_array_equal(targets, [0, 0])
    moved = session.engine.transform([0, 0, 1, 0, 0, 0, 1, 1, 1])
    output = binding.resolve(session.engine, meshes, [moved, translated], targets, records)
    np.testing.assert_allclose(output[:, [3, 7, 11]], [[0, 0, 1.8], [2, 0, 1.8]])


def test_bound_surface_vertex_deformation_moves_point_and_retains_offset(session):
    vertices = [[0, 0, 0], [1, 0, 0], [0, 1, 0]]
    before = session.engine.create_mesh(vertices, [0, 1, 2], [0, 3])
    targets, records = binding.capture(
        session.engine, [before.handle], [IDENTITY], [[0.25, 0.25, 0.1]]
    )
    after = session.engine.create_mesh([[0, 0, 2], [1, 0, 2], [0, 1, 2]], [0, 1, 2], [0, 3])
    output = binding.resolve(session.engine, [after.handle], [IDENTITY], targets, records)
    np.testing.assert_allclose(output[0, [3, 7, 11]], [0.25, 0.25, 2.1])


def test_capture_and_resolution_cancel_or_reject_missing_surface(session, cube):
    args = (session.engine, [cube.handle], [IDENTITY])
    targets, records = binding.capture(*args, [[0, 0, 1]])
    with pytest.raises(ValueError, match="missing"):
        binding.resolve(*args, [1], records)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        binding.capture(*args, [[0, 0, 1]], cancel=cancel.handle)
    with pytest.raises(ValueError, match="cancel"):
        binding.resolve(*args, targets, records, cancel.handle)
