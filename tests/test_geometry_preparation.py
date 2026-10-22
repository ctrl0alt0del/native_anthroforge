"""Deferred native pipelines preserve geometry, query, cancellation and ownership contracts."""

import weakref
from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application.assets import Asset
from anthroforge.application.primitive_operations import default_primitive
from anthroforge.core.construction import (
    BodyPiece,
    Control,
    Curve,
    CurvePoint,
    Deformer,
    Target,
    Thickness,
)
from anthroforge.core.entities import IDENTITY
from anthroforge.native import bodies, components, topology
from anthroforge.native import construction as native
from anthroforge.native.base_cache import BaseCache
from anthroforge.native.mesh import GeometryEngine, NativeCancellation


@pytest.fixture
def engine():
    value = GeometryEngine()
    yield value
    value.bases.clear()


def curve(closed):
    points = ((0, 0, 0), (0.4, 0.3, 0.2), (0.9, -0.1, 0.1), (0.5, -0.4, 0))
    return Curve(
        tuple(CurvePoint(position=p, radius=0.8 + i / 5, tilt=i / 4) for i, p in enumerate(points)),
        closed=closed,
    )


def deform(mesh):
    engine = mesh.engine
    binding = Deformer("HOOK", "control", Target("owner"), strength=0.4, radius=2, falloff="SMOOTH")
    matrix = engine.transform([0.1, -0.05, 0.2, 12, -8, 17, 1.2, 0.8, 1.1])
    points = native.hook(engine, mesh.array(0), binding, IDENTITY, matrix, 0)
    cage = Control(
        "Cage", "LATTICE", points=tuple(map(tuple, native.lattice_grid(engine, (2, 2, 2))))
    )
    cage = replace(cage, points=(*cage.points[:-1], (0.6, 0.4, 0.8)))
    binding = replace(binding, kind="LATTICE", control=cage.id)
    points = native.lattice(engine, points, cage, binding, IDENTITY, IDENTITY, 0)
    return native.deformed(mesh, points)


def pipeline(engine, shape, closed, shell, complete):
    path = curve(closed)
    piece = BodyPiece(path.id, shape, fit=False, position=0.05, width=0.13, depth=0.09)
    base = bodies.base if complete else bodies.draft_base
    mesh = deform(base(engine, piece, 17, closed, 0))
    mesh = bodies.bend(mesh, bodies.path(engine, path, 0), piece, closed, 0)
    matrix = engine.transform([0.3, -0.2, 0.1, 21, 32, -12, 0.8, 1.2, 1.1])
    mesh = native.deformed(mesh, components.transformed(engine, mesh.array(0), matrix))
    if shell:
        mesh = native.solidify(mesh, Thickness(even=True, high_quality_normals=True, clamp=0.1), 0)
    return mesh


def equivalent(expected, actual):
    assert expected.counts == actual.counts
    for kind in range(5):
        np.testing.assert_allclose(actual.array(kind), expected.array(kind), rtol=0, atol=1e-12)
    np.testing.assert_allclose(actual.bounds, expected.bounds, rtol=0, atol=1e-12)
    for y in (-0.2, 0, 0.2):
        ray = ([0.5, y, 2], [0, 0, -1])
        a, b = (mesh.engine.pick(mesh, IDENTITY, *ray) for mesh in (expected, actual))
        assert (a is None) == (b is None)
        if a is not None:
            np.testing.assert_allclose(a, b, rtol=0, atol=1e-12)


@pytest.mark.parametrize("shape", ["BOX", "CYLINDER", "CAPSULE"])
@pytest.mark.parametrize("closed", [False, True])
@pytest.mark.parametrize("shell", [False, True])
def test_deferred_pipeline_matches_prepared_stages(engine, shape, closed, shell):
    expected = pipeline(engine, shape, closed, shell, True)
    draft = pipeline(engine, shape, closed, shell, False)
    assert draft.counts[-1] == 0
    with pytest.raises(ValueError, match="finalized"):
        engine.pick(draft, IDENTITY, [0, 0, 2], [0, 0, -1])
    equivalent(expected, topology.finalize(draft, expected, 0))
    assert draft.counts[-1] == 0


def test_cancelled_finalization_does_not_mutate_shared_base(engine):
    piece = BodyPiece("curve")
    draft = bodies.draft_base(engine, piece, 32, False, 0)
    cancel = NativeCancellation(engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancelled"):
        topology.finalize(draft, None, cancel.handle)
    equivalent(bodies.base(engine, piece, 32, False, 0), topology.finalize(draft, None, 0))
    assert bodies.draft_base(engine, piece, 32, False, 0) is draft


def test_asset_boundary_rejects_unfinished_geometry(engine):
    draft = bodies.draft_base(engine, BodyPiece("curve"), 32, False, 0)
    with pytest.raises(ValueError, match="finalized"):
        Asset(draft, "generated", "", 1.0, False)
    ready = topology.finalize(draft, None, 0)
    assert Asset(ready, "generated", "", 1.0, False).mesh is ready


def test_generated_concave_quad_uses_valid_initial_diagonal(engine):
    points = [[0, 0, 0], [1, 0.25, 0], [2, 0, 0], [1, 2, 0]]
    source = engine.create_mesh(points, [0, 1, 2, 3], [0, 4])
    mesh = native.joined(engine, [source], 0)
    np.testing.assert_array_equal(mesh.array(3), [[0, 1, 3], [1, 2, 3]])
    assert engine.pick(mesh, IDENTITY, [0.5, 0.05, 1], [0, 0, -1]) is None
    assert engine.pick(mesh, IDENTITY, [1, 1, 1], [0, 0, -1]) is not None
    moved = native.deformed(mesh, [[0, 0, 0], [1, -1, 0], [2, 0, 0], [1, 2, 0]])
    np.testing.assert_array_equal(moved.array(3), mesh.array(3))
    np.testing.assert_array_equal(topology.finalize(moved, mesh, 0).array(3), mesh.array(3))


@pytest.mark.parametrize(
    "field,value", [("shape", "BOX"), ("sides", 12), ("width", 0.2), ("depth", 0.3), ("length", 2)]
)
def test_base_cache_distinguishes_shape_inputs(engine, field, value):
    piece = BodyPiece("curve")
    original = bodies.draft_base(engine, piece, 32, False, 0)
    changed = bodies.draft_base(engine, replace(piece, **{field: value}), 32, False, 0)
    assert original is not changed
    assert bodies.draft_base(engine, piece, 33, False, 0) is not original
    assert bodies.draft_base(engine, piece, 32, True, 0) is not original
    assert (
        bodies.draft_base(engine, replace(piece, fit=False, position=2), 32, False, 0) is original
    )


def test_cache_eviction_releases_only_unowned_geometry(engine):
    engine.bases = BaseCache(budget=100000, capacity=1)
    first = bodies.draft_base(engine, BodyPiece("a"), 32, False, 0)
    ref = weakref.ref(first)
    second = bodies.draft_base(engine, BodyPiece("b", width=0.2), 32, False, 0)
    assert len(engine.bases.items) == 1 and engine.bases.bytes <= engine.bases.budget
    assert topology.finalize(first, None, 0).counts[-1] > 0
    del first
    assert ref() is None
    engine.bases.clear()
    assert engine.bases.bytes == 0 and second.array(0).shape[0] > 0


@pytest.mark.parametrize("closed", [False, True])
def test_loft_join_and_imported_drafts_preserve_output(engine, closed):
    definition = default_primitive("LOFT", "CAPSULE")
    first = curve(closed)
    second = replace(curve(closed), matrix=engine.transform([0, 0, 0.3, 0, 0, 0, 1, 1, 1]))
    definition = replace(definition, curves=(first, second), caps=closed)
    samples = [native.sample_curve(engine, c, definition) for c in definition.curves]
    ready = native.loft(engine, definition, samples, 0)
    draft = native.loft(engine, definition, samples, 0, complete=False)
    imported = engine.create_mesh(ready.array(0), ready.array(1), ready.array(2))
    expected = native.joined(engine, [deform(ready), deform(imported)], 0)
    actual = native.joined(engine, [deform(draft), deform(topology.draft(imported, 0))], 0)
    actual = topology.finalize(actual, expected, 0)
    equivalent(expected, actual)
