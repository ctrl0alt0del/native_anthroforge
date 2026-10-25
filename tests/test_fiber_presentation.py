"""World radius is presentation state, never an anatomical or routing parameter."""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from zipfile import ZipFile

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import path_display, paths
from tests.test_quick_fiber import cube, placed


def line(session, closed=False):
    positions = [(0, 0, 0), (0, 0, 1)] if not closed else [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
    curve = Curve(
        tuple(CurvePoint(position=p) for p in positions),
        engine_settings=PolylineSettings(),
        closed=closed,
    )
    return paths.evaluate(session.engine, curve)


@pytest.mark.parametrize("scale", [(1, 1, 1), (3, 7, 2), (-3, 7, 2)])
def test_world_radius_is_independent_of_parent_scale_and_mesh_has_bounds(session, scale):
    path = line(session)
    frame = session.engine.transform([2, -1, 4, 0, 0, 0, *scale])
    mesh = path_display.tube(path, frame, 0.2)
    points = mesh.array(0).reshape(2, 12, 3)
    centers = np.array([[2, -1, 4], [2, -1, 4 + scale[2]]])
    np.testing.assert_allclose(
        np.linalg.norm(points - centers[:, None, :], axis=2), 0.2, atol=1e-12
    )
    np.testing.assert_allclose(mesh.bounds[:3], points.reshape(-1, 3).min(axis=0))
    np.testing.assert_allclose(mesh.bounds[3:], points.reshape(-1, 3).max(axis=0))
    assert mesh.prepared and mesh.counts[4] > 0


def test_closed_tube_shares_its_seam_and_invalid_radius_is_rejected(session):
    path = line(session, True)
    mesh = path_display.tube(path, IDENTITY, 0.02)
    assert mesh.counts[0] == 36 and mesh.counts[1] == 36
    with pytest.raises(ValueError, match="positive radius"):
        path_display.tube(path, IDENTITY, 0)


def test_radius_changes_only_workspace_and_survives_saving(session, tmp_path):
    fiber = placed(session, cube(session))
    objects, cursor, jobs = (
        session.document.objects,
        session.history.cursor,
        len(session.scheduler.jobs),
    )
    session.command("fiber.presentation", target=fiber.id, radius=0.025)
    assert session.document.objects == objects and session.history.cursor == cursor
    assert len(session.scheduler.jobs) == jobs
    roundtrip(session, tmp_path / "radius.anthroforge")
    assert session.command("fiber.presentation.inspect", target=fiber.id)["radius"] == 0.025
    assert session.document.object(fiber.id).result == fiber.result


def roundtrip(session, path):
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(path))
    session.wait()


def test_radius_validation_and_distinct_workspace_styles(session):
    fiber = placed(session, cube(session))
    with pytest.raises(ValueError, match="nonnegative"):
        session.command("fiber.presentation", target=fiber.id, radius=-1)
    original = session.workspace
    session.command("fiber.presentation", target=fiber.id, radius=0)
    assert session.workspace.fibers[0].radius == 0
    assert replace(session.workspace, fibers=()) == original


def test_repeated_worker_tube_calls_are_all_attributed_without_changing_geometry(session, tmp_path):
    path = line(session)
    session.command("profile.start")
    with ThreadPoolExecutor(4) as workers:
        meshes = list(workers.map(lambda _: path_display.tube(path, IDENTITY, 0.01), range(32)))
    result = session.command("profile.stop", path=str(tmp_path / "native.afprofile.zip"), wait=True)
    with ZipFile(result["path"]) as archive:
        summary = json.loads(archive.read("summary.json"))
    assert len(meshes) == summary["durations"]["native/af_path_display_tube"]["count"] == 32
