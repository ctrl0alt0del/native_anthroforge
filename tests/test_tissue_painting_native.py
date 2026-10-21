"""Visibility, material domains and rate-independent strokes exercise real native geometry."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import painting, tissue_shapes
from tests.conftest import CUBE

VIEW = (0, 0, 4, 1, 0, 0, 0, 1, 0, 0, 0, -1, 100, 1)


def cube(session, others=(), frames=()):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    inputs = painting.Inputs(mesh, mesh, False, mesh.counts[0], IDENTITY, VIEW, others, frames)
    return mesh, painting.prepare(inputs)


def stroke(prepared, points=((0, 0),), through=False):
    return painting.PaintColors(
        prepared, np.zeros(prepared.count), points, [100, 1, 1, 1, through], 0
    )


def test_visible_paint_excludes_back_surface_but_through_reaches_it(session):
    mesh, prepared = cube(session)
    visible, through = stroke(prepared), stroke(prepared, through=True)
    z = mesh.array(0)[:, 2]
    assert np.all(visible.values[z == z.min()] == 0)
    assert np.all(visible.values[z == z.max()] > 0)
    assert np.all(through.values > 0)
    assert visible.chunks and prepared.bytes > 0


def test_visible_paint_respects_other_displayed_geometry(session):
    occluder = session.engine.create_mesh(
        [[-2, -2, 3], [2, -2, 3], [2, 2, 3], [-2, 2, 3]], [0, 1, 2, 3], [0, 4]
    )
    _, prepared = cube(session, (occluder,), (IDENTITY,))
    assert not np.any(stroke(prepared).values)
    assert np.all(stroke(prepared, through=True).values > 0)


def test_stroke_frequency_does_not_accumulate_extra_weight(session):
    _, prepared = cube(session)
    sparse = stroke(prepared, ((-30, 0), (30, 0)), True)
    dense = stroke(prepared, tuple((x, 0) for x in range(-30, 31)), True)
    np.testing.assert_allclose(sparse.values, dense.values, rtol=0, atol=1e-14)


def test_single_base_sample_remains_one_material_weight(session):
    shape = tissue_shapes.radial(session.engine, IDENTITY, TissueInflation(mode="RADIAL"), 24)
    prepared = painting.prepare(painting.Inputs(shape, None, True, 1, IDENTITY, VIEW))
    result = stroke(prepared)
    assert len(result.values) == 1 and result.values[0] > 0


def test_invalid_stroke_dimensions_and_nonfinite_values_are_rejected(session):
    _, prepared = cube(session)
    with pytest.raises(ValueError):
        stroke(prepared, ((float("nan"), 0),))
    with pytest.raises(ValueError):
        painting.PaintColors(prepared, [], [[0, 0]], [20, 1, 1, 1, 0], 0)
