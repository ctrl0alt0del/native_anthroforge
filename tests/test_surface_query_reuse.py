"""Source reuse must preserve the complete exterior-only placement contract."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import construction, surface_queries, tissue_inflation, tissue_shapes
from anthroforge.native.mesh import NativeCancellation
from tests.test_surface_query_modes import capture, compound, material_point
from tests.test_tissue_inflation import grid_mesh


def cube(engine):
    return engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)


def confirmed(source, base=None):
    return surface_queries.prepare(source, base, surface_queries.Mode.CONFIRMED)


def shares_geometry(query, source):
    return query.mesh.array(0).ctypes.data == source.array(0).ctypes.data


@pytest.mark.parametrize("kind", ["cube", "radial", "disjoint", "open"])
def test_qualified_geometry_reuses_owned_mesh_and_original_bindings(session, kind):
    source = clean_mesh(session.engine, kind)
    query = confirmed(source)
    assert shares_geometry(query, source)
    np.testing.assert_array_equal(query.mesh.array(3), source.array(3))
    before = capture(query, [0.1, 0.2, 1.1])[1]
    session.engine.clear_caches()
    np.testing.assert_array_equal(capture(query, [0.1, 0.2, 1.1])[1], before)


def clean_mesh(engine, kind):
    if kind == "cube":
        return cube(engine)
    if kind == "radial":
        return tissue_shapes.radial(engine, IDENTITY, TissueInflation(amount=0.5), 128)
    if kind == "disjoint":
        return compound(engine, scale=1, shift=3, reverse=False)
    return engine.create_mesh([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [0, 1, 2], [0, 3])


@pytest.mark.parametrize("reverse", [True, False])
def test_nesting_is_not_qualified_even_without_intersections(session, reverse):
    source = compound(session.engine, reverse=reverse)
    query = confirmed(source)
    assert not shares_geometry(query, source)
    assert query.mesh.counts[3] == 12
    _, records = capture(query, [0.1, 0, 0])
    assert np.linalg.norm(material_point(source, records[0])) == pytest.approx(0.5)


def test_reversed_closed_surface_requires_normal_correction(session):
    original = cube(session.engine)
    faces = original.array(3)[:, ::-1]
    source = session.engine.create_mesh(original.array(0), faces.ravel(), np.arange(13) * 3)
    query = confirmed(source)
    assert not shares_geometry(query, source)
    triangles = query.mesh.array(0)[query.mesh.array(3)]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    assert np.all(np.einsum("ij,ij->i", normals, triangles.mean(axis=1)) > 0)


def test_duplicate_seam_vertices_use_full_cleanup(session):
    original = cube(session.engine)
    vertices = original.array(0)[original.array(3)].reshape(-1, 3)
    source = session.engine.create_mesh(vertices, np.arange(36), np.arange(13) * 3)
    query = confirmed(source)
    assert not shares_geometry(query, source)
    assert query.mesh.counts[0] == 8 and query.mesh.counts[3] == 12
    _, records = capture(query, [0.1, 0, 0])
    assert np.linalg.norm(material_point(source, records[0])) == pytest.approx(0.5)


def open_tissue(engine):
    base = grid_mesh(engine, [[[0, 0, 0], [0, 1, 0]], [[1, 0, 0], [1, 1, 0]]])
    source = tissue_inflation.evaluate(base, TissueInflation(enabled=False))
    return base, construction.deformed(source, base.array(0) + [0, 0, 0.2])


def test_temporary_closure_is_checked_but_not_exposed_as_attachment_geometry(session):
    base, source = open_tissue(session.engine)
    query = confirmed(source, base)
    assert shares_geometry(query, source)
    assert query.mesh.counts == source.counts
    _, records = capture(query, [0.5, 0.5, -0.1])
    assert material_point(source, records[0])[2] == pytest.approx(0.2)


def test_changed_geometry_cannot_reuse_previous_qualification(session):
    source = cube(session.engine)
    before = confirmed(source)
    inverted = construction.deformed(source, -source.array(0))
    after = confirmed(inverted)
    assert shares_geometry(before, source)
    assert not shares_geometry(after, inverted)
    assert confirmed(source) is before and confirmed(inverted) is after


def test_changed_backing_cannot_reuse_previous_qualification(session):
    base, source = open_tissue(session.engine)
    before = confirmed(source, base)
    moved = construction.deformed(base, base.array(0) + [0, 0, 1])
    after = confirmed(source, moved)
    assert shares_geometry(before, source)
    assert not shares_geometry(after, source)
    assert confirmed(source, base) is before


def test_cancelled_clean_query_does_not_install_cache_entry(session):
    source = cube(session.engine)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED, cancel.handle)
    assert not session.engine.surface_queries.items
    assert shares_geometry(confirmed(source), source)


def test_shared_query_allocation_is_counted_once(session):
    source = cube(session.engine)
    query = confirmed(source)
    size = surface_queries.retained_bytes(session.engine, (source,))
    assert size > source.array(0).nbytes + source.array(3).nbytes
    assert query.bytes == size == session.engine.surface_queries.bytes


def test_cleaned_query_counts_both_its_own_and_source_allocation(session):
    source = compound(session.engine)
    query = confirmed(source)
    sizes = [surface_queries.retained_bytes(session.engine, (m,)) for m in (source, query.mesh)]
    assert min(sizes) > 0 and query.bytes == sum(sizes)


def test_query_cache_honors_byte_budget_and_live_query_ownership(session):
    source = cube(session.engine)
    first = confirmed(source)
    session.engine.surface_queries.budget = first.bytes
    other = construction.deformed(source, source.array(0) + [2, 0, 0])
    second = confirmed(other)
    assert session.engine.surface_queries.bytes <= first.bytes
    assert len(session.engine.surface_queries.items) == 1
    assert next(iter(session.engine.surface_queries.items.values()))[0] is second
    assert capture(first, [0.1, 0, 0])[1].shape == (1, 28)


def test_query_larger_than_budget_remains_usable_but_is_not_cached(session):
    session.engine.surface_queries.budget = 1
    source = cube(session.engine)
    query = confirmed(source)
    assert not session.engine.surface_queries.items and session.engine.surface_queries.bytes == 0
    assert capture(query, [0.1, 0, 0])[1].shape == (1, 28)
