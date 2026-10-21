"""Confirmed queries select exterior fragments but retain original material bindings."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import point_attachments, surface_queries, tissue_parts
from anthroforge.native.mesh import NativeCancellation
from tests.test_tissue_intersection_policy import fixture


def compound(engine, scale=0.5, shift=0, reverse=True):
    cube = engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)
    vertices, faces = cube.array(0).copy(), cube.array(3).copy()
    inner = faces[:, ::-1] if reverse else faces
    both = np.concatenate((faces, inner + len(vertices)))
    return engine.create_mesh(
        np.concatenate((vertices, scale * vertices + [shift, 0, 0])),
        both.ravel(),
        np.arange(0, both.size + 1, 3),
    )


def capture(query, point):
    engine = query.mesh.engine
    return point_attachments.capture(engine, [query.mesh.handle], [IDENTITY], [point])


def material_point(source, binding):
    return (source.array(0)[binding[:3].astype(int)] * binding[3:6, None]).sum(axis=0)


def test_confirmed_excludes_sealed_cavity_and_preserves_original_coordinates(session):
    source = compound(session.engine)
    preview = surface_queries.prepare(source, None, surface_queries.Mode.PREVIEW)
    confirmed = surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED)
    _, raw = capture(preview, [0.1, 0, 0])
    owners, clean = capture(confirmed, [0.1, 0, 0])
    assert np.linalg.norm(material_point(source, raw[0])) == pytest.approx(0.25)
    assert np.linalg.norm(material_point(source, clean[0])) == pytest.approx(0.5)
    resolved = point_attachments.resolve(session.engine, [source.handle], [IDENTITY], owners, clean)
    np.testing.assert_allclose(resolved[0, [3, 7, 11]], [0.1, 0, 0], atol=1e-12)
    assert source.counts[3] == 24 and confirmed.mesh.counts[3] == 12


def test_overlapping_components_exclude_buried_faces(session):
    source = compound(session.engine, scale=1, shift=0.5, reverse=False)
    query = surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED)
    _, records = capture(query, [0.49, 0, 0])
    location = material_point(source, records[0])
    assert np.linalg.norm(location - [0.49, 0, 0]) >= 0.49


def test_open_zero_volume_surface_is_still_a_valid_target(session):
    source = session.engine.create_mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [0, 1, 2], [0, 3])
    query = surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED)
    _, records = capture(query, [0.2, 0.2, 0.1])
    np.testing.assert_allclose(material_point(source, records[0]), [0.2, 0.2, 0])


def test_crossed_tissue_uses_temporary_backing_and_original_material(session):
    base, parts = fixture(session.engine)
    source = tissue_parts.evaluate(base, parts, "a", True)
    before = source.array(0).copy()
    query = surface_queries.prepare(source, base, surface_queries.Mode.CONFIRMED)
    _, records = capture(query, source.array(0)[852] + [0, 0, 0.1])
    assert np.all(records[:, :3] < len(before))
    np.testing.assert_array_equal(source.array(0), before)
    assert query.mesh.counts[3] > 0 and not query.mesh.counts[3] == source.counts[3]


def test_queries_are_cached_owned_and_cancel_before_boolean(session):
    source = compound(session.engine)
    first = surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED)
    assert surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED) is first
    session.engine.clear_caches()
    assert capture(first, [1, 0, 0])[1].shape == (1, 28)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED, cancel.handle)
