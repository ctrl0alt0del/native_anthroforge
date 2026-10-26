"""Centerlines are explicit native sources, independent of viewport tube styling."""

from dataclasses import replace

import numpy as np

from anthroforge.application import skin_capture
from anthroforge.core.fiber_presentation import FiberPresentation
from anthroforge.native import skin_fields, skin_gaps
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.skin_capture import capture_sources
from tests.test_fiber_creation import bind, scene
from tests.test_fiber_presentation import line


def line_source(engine):
    xyz = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0]])
    faces = np.empty((0, 3), dtype=np.int64)
    owners = np.empty(0, dtype=np.int32)
    return skin_gaps.create(
        engine, xyz, faces, owners, [[0, 1, 0]], segments=[[0, 1], [1, 2]], segment_owners=[0, 0]
    )


def test_line_queries_and_bindings_preserve_segment_identity():
    engine = GeometryEngine()
    source = line_source(engine)
    np.testing.assert_allclose(source.sample([[0.5, 0.25, 0]], 10)[0, 0], 0.25)
    mesh = engine.create_mesh([[0.5, 0.25, 0], [0.4, 0.25, 0], [0.5, 0.3, 0]], [0, 1, 2], [0, 3])
    bindings = source.bind(mesh)
    np.testing.assert_array_equal(bindings["kinds"][:, 0], 1)
    np.testing.assert_array_equal(bindings["triangles"][:, 0], 0)
    np.testing.assert_allclose(bindings["barycentric"][0, 0], [0.5, 0.5, 0])
    np.testing.assert_allclose(bindings["offsets"][0], 0.25)
    source.close()


def test_centerline_only_envelope_is_finite_and_retains_path_bindings():
    engine = GeometryEngine()
    xyz = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0]])
    faces = np.empty((0, 3), dtype=np.int64)
    fields = skin_fields.prepare(
        engine, xyz, faces, [], np.ones(3), resolution=24, segments=[[0, 1], [1, 2]]
    )
    source = line_source(engine)
    result = source.envelope(fields)
    assert np.isfinite(result.mesh.array(0)).all() and result.mesh.counts[0] > 0
    assert np.all(source.bind(result.mesh)["kinds"][:, 0] == 1)
    fields.close()
    source.close()


def test_fiber_capture_contains_no_tube_mesh(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    captured = skin_capture.capture(session.engine, session.document, session.resources)
    index = next(i for i, row in enumerate(captured.sources) if row.identity.owner == fiber.id)
    assert index not in captured.geometry.owners
    assert set(captured.geometry.segment_owners) == {index}
    path = session.resources.paths[fiber.result.asset].path
    assert len(captured.geometry.segments) == path.count - 1
    selected = captured.geometry.segments[:, 0]
    np.testing.assert_allclose(captured.geometry.vertices[selected], path.array()[:-1, :3])


def test_workspace_radius_cannot_change_skin_capture(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    document = session.document
    first = skin_capture.capture(session.engine, document, session.resources)
    workspace = replace(document.workspaces[0], fibers=(FiberPresentation(fiber.id, 2.0),))
    changed = replace(document, workspaces=(workspace,))
    second = skin_capture.capture(session.engine, changed, session.resources)
    for key in ("vertices", "triangles", "segments", "policies"):
        np.testing.assert_array_equal(getattr(first.geometry, key), getattr(second.geometry, key))


def test_closed_centerline_capture_preserves_closure_and_reflected_positions(session):
    path = line(session, True)
    matrix = np.eye(4)
    matrix[0, 0], matrix[2, 2], matrix[0, 3] = -2, 3, 4
    captured = capture_sources(session.engine, [path], [1], [matrix.ravel()], [[0, 1, 0]])
    assert captured.triangles.shape == (0, 3)
    np.testing.assert_array_equal(captured.segments, [[0, 1], [1, 2], [2, 0]])
    expected = path.array()[:, :3] @ matrix[:3, :3].T + matrix[:3, 3]
    np.testing.assert_allclose(captured.vertices, expected)
    np.testing.assert_array_equal(captured.segment_owners, 0)
