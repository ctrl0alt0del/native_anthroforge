"""Outward placement is distinct from exact picking and survives curve precision."""

from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import routing, scene, strokes
from tests.test_snapped_routing import require_clear


def cube(session):
    return session.engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)


def hit(session, mesh, frame, origin, ray):
    return scene.pick(
        session.engine,
        np.array([mesh.handle], dtype=np.uint64),
        np.array([frame], dtype=float),
        origin,
        ray,
    )[0]


@pytest.mark.parametrize("scale", [(1, 1, 1), (-2, 3, 0.7), (0.001, 0.002, 0.003)])
@pytest.mark.parametrize("offset", [-0.2, 0, 0.02])
def test_snaps_outward_with_nonuniform_and_reflected_transforms(session, scale, offset):
    mesh = cube(session)
    frame = session.engine.transform([2, -3, 5, 21, 37, 11, *scale])
    start = session.engine.world_point(frame, [0.17, 0.23, 2])
    target = session.engine.world_point(frame, [0.17, 0.23, 0.5])
    row = hit(session, mesh, frame, start, np.array(target) - start)
    snap = scene.surface_snap(session.engine, mesh.handle, frame, int(row[3]), row[5:8], offset)
    normal = np.array(snap["normal"])
    assert np.dot(np.array(snap["point"]) - row[5:8], normal) > max(offset, 0)
    assert np.dot(np.asarray(snap["point"], dtype=np.float32) - target, normal) > 0
    assert row[5:8] == pytest.approx(target, abs=1e-12)


def test_backface_snap_uses_surface_orientation_not_camera(session):
    mesh = cube(session)
    row = hit(session, mesh, IDENTITY, [0.1, 0.2, 0], [0, 0, 1])
    snap = scene.surface_snap(session.engine, mesh.handle, IDENTITY, int(row[3]), row[5:8])
    assert snap["point"][2] > 0.5 and snap["normal"][2] == 1


@pytest.mark.parametrize("projection", [False, True])
def test_drawing_and_point_snapping_share_outward_policy(session, projection):
    mesh = cube(session)
    stroke = strokes.Stroke(
        session.engine, [mesh.handle], [IDENTITY], [0, 0, 0, 0, 0, 1], [projection, 0, -0.1, 0]
    )
    stroke.snapping(not projection)
    row = stroke.probe([0.1, 0.2, 2, 0, 0, -1, 20, 40, 1])
    assert row[2] > 0.5
    assert np.float32(row[2]) > 0.5


def test_routing_between_outward_snapped_opposite_faces_has_clear_segments(session):
    mesh = cube(session)
    points = []
    for start, ray in (([0.12, 0.2, 2], [0, 0, -1]), ([0.1, 0.2, -2], [0, 0, 1])):
        row = hit(session, mesh, IDENTITY, start, ray)
        snap = scene.surface_snap(session.engine, mesh.handle, IDENTITY, int(row[3]), row[5:8])
        points.append(CurvePoint(position=tuple(snap["point"])))
    curve = Curve(tuple(points), engine_settings=RoutingSettings())
    value = routing.Inputs(curve, (mesh.handle,), (IDENTITY,))
    path, _ = routing.evaluate(session.engine, value)
    require_clear(session, path, value)


def test_pick_retains_double_precision_barycentric_surface_location(session):
    mesh = session.engine.create_mesh([[9, 3, 1.3], [11, 3, 1.3], [9, 5, 1.3]], [0, 1, 2], [0, 3])
    row = hit(session, mesh, IDENTITY, [9.746251752, 3.203587, 5], [0, 0, -1])
    assert row[5:8] == pytest.approx([9.746251752, 3.203587, 1.3], abs=1e-14)
