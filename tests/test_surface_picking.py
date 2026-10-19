"""Axis-parallel rays hit flat surfaces and deformed shared edges without a mesh scan."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import IDENTITY
from anthroforge.native import curve_surfaces, paths, scene, topology


def mesh(session, axis, changed):
    rows = []
    for z in (-0.3, 0.3):
        points = [[-0.6, 0, 0.6 if changed and z > 0 else z], [0.6, 0, z]]
        points = np.roll(points, axis - 1, axis=1)
        curve = Curve(tuple(CurvePoint(position=tuple(p)) for p in points))
        rows.append(
            curve_surfaces.row(paths.evaluate(session.engine, curve), IDENTITY, CurveUse(curve.id))
        )
    settings = curve_surfaces.Settings()
    _, across = curve_surfaces.layout(session.engine, rows, settings)
    draft = curve_surfaces.geometry(session.engine, rows, across, settings)
    return topology.finalize(draft, None, 0)


def query(session, item, origin, direction):
    return scene.pick(
        session.engine,
        np.array([item.handle], dtype=np.uint64),
        np.array([IDENTITY]),
        origin,
        direction,
    )


@pytest.mark.parametrize("axis", [0, 1, 2])
@pytest.mark.parametrize("sign", [-1, 1])
@pytest.mark.parametrize("changed", [False, True])
def test_surface_axis_view_rays_hit_center_and_boundary(session, axis, sign, changed):
    item = mesh(session, axis, changed)
    direction = np.eye(3)[axis] * sign
    vertices = item.array(0)
    for position in (np.zeros(3), *vertices[::24]):
        hits = query(session, item, position - 2 * direction, direction)
        assert hits, (axis, sign, changed, position)
        np.testing.assert_allclose(hits[0][5:8], position, atol=2e-7)
    assert not query(session, item, np.ones(3) * 5, direction)


@pytest.mark.parametrize("direction", [[0, 0, 0], [float("nan"), 0, 1]])
def test_invalid_pick_ray_is_rejected(session, direction):
    item = mesh(session, 1, False)
    with pytest.raises(ValueError, match="finite nonzero ray"):
        query(session, item, [0, -2, 0], direction)
