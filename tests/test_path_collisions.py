"""Native segment queries catch unsampled crossings and containment without editing paths."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import path_collisions, paths
from anthroforge.native.mesh import NativeCancellation


def query(session, assembly, points, owners=None, frame=IDENTITY, closed=False):
    curve = Curve(
        tuple(CurvePoint(position=tuple(p)) for p in points),
        closed=closed,
        engine_settings=PolylineSettings(),
    )
    path = paths.evaluate(session.engine, curve)
    mesh = session.assets[session.document.entity(assembly[0]).asset].mesh
    row = path_collisions.row(path, frame, owners or [0] * len(points))
    result, tolerance = path_collisions.check(session.engine, [row], [mesh.handle], [frame])
    assert tolerance > 0
    return result[0, 0], path.array()[:, :3]


@pytest.mark.parametrize(
    "points,expected",
    [
        ([[-2, 0, 0], [2, 0, 0]], 0),
        ([[-0.2, 0, 0], [0.2, 0, 0]], 0),
        ([[-2, 0, 0.6], [2, 0, 0.6]], -1),
    ],
)
def test_crossing_containment_and_clear_path(session, assembly, points, expected):
    found, unchanged = query(session, assembly, points)
    assert found == expected
    np.testing.assert_allclose(unchanged, points)


def test_contact_exemption_is_local_and_does_not_hide_other_crossings(session, assembly):
    assert query(session, assembly, [[-0.5, 0, 0], [-2, 0, 0]], [1, 0])[0] == -1
    assert query(session, assembly, [[-0.5, 0, 0], [2, 0, 0]], [1, 0])[0] == 0


def test_closed_last_segment_is_checked(session, assembly):
    points = [[-1, -1, 0], [-1, 1, 0], [1, 1, 0]]
    assert query(session, assembly, points, closed=True)[0] == 2


def test_nonuniform_affine_frames_preserve_collision(session, assembly):
    frame = session.engine.transform([5, 7, 3, 15, 25, 40, 2, 0.5, 3])
    assert query(session, assembly, [[-2, 0, 0], [2, 0, 0]], frame=frame)[0] == 0


def test_collision_query_is_cooperatively_cancellable(session, assembly):
    curve = Curve((CurvePoint(), CurvePoint(position=(1, 0, 0))))
    path = paths.evaluate(session.engine, curve)
    row = path_collisions.row(path, IDENTITY, [0, 0])
    mesh = session.assets[session.document.entity(assembly[0]).asset].mesh
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        path_collisions.check(session.engine, [row], [mesh.handle], [IDENTITY], cancel.handle)
