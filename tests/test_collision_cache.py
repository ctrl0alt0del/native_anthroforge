"""Cached misses and hits remain exact across paths, contacts, transforms and removal."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import path_collisions as collision
from anthroforge.native import paths
from anthroforge.native.mesh import NativeCancellation, doubles


def fixture(session, assembly):
    mesh = session.assets[session.document.entity(assembly[0]).asset].mesh
    curve = Curve(
        tuple(CurvePoint(position=(x, 0, 0)) for x in (-2, 2)), engine_settings=PolylineSettings()
    )
    path = paths.evaluate(session.engine, curve)
    rows = [collision.row(path, IDENTITY, [0, 0])]
    frames = [IDENTITY, session.engine.transform([0, 0, 0, 0, 0, 0, 20, 20, 20])]
    return rows, [mesh.handle] * 2, frames


def compare(engine, rows, meshes, frames):
    actual, tolerance = collision.check(engine, rows, meshes, frames)
    expected, reference = collision.invoke(
        engine, rows, np.asarray(meshes, dtype=np.uint64), doubles(frames), 0
    )
    np.testing.assert_array_equal(actual, expected)
    assert tolerance == reference
    return actual


def test_unchanged_pairs_reuse_evidence_and_moving_obstacle_invalidates_miss(session, assembly):
    rows, meshes, frames = fixture(session, assembly)
    events = []
    session.engine.collision_checks.observer = lambda action, **data: events.append((action, data))
    compare(session.engine, rows, meshes, frames)
    compare(session.engine, rows, meshes, frames)
    assert events[-1][1]["reason"] == "hit=2,miss=0"
    frames[0] = session.engine.transform([0, 2, 0, 0, 0, 0, 1, 1, 1])
    assert compare(session.engine, rows, meshes, frames)[0, 0] == -1
    assert events[-1][1]["reason"] == "hit=1,miss=1"
    frames[0] = IDENTITY
    assert compare(session.engine, rows, meshes, frames)[0, 0] == 0
    assert events[-1][1]["reason"] == "hit=1,miss=1"


def test_removed_reordered_targets_and_changed_tolerance_match_fresh_query(session, assembly):
    rows, meshes, frames = fixture(session, assembly)
    compare(session.engine, rows, meshes, frames)
    compare(session.engine, rows, meshes[::-1], frames[::-1])
    compare(session.engine, rows, meshes[:1], frames[:1])
    frames[1] = session.engine.transform([0, 0, 0, 0, 0, 0, 200, 200, 200])
    compare(session.engine, rows, meshes, frames)


def test_cancelled_warm_cache_cannot_publish_success(session, assembly):
    rows, meshes, frames = fixture(session, assembly)
    compare(session.engine, rows, meshes, frames)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        collision.check(session.engine, rows, meshes, frames, cancel.handle)
    compare(session.engine, rows, meshes, frames)


def test_path_transform_and_contact_membership_invalidate_reused_row(session, assembly):
    rows, meshes, frames = fixture(session, assembly)
    compare(session.engine, rows, meshes, frames)
    path = rows[0]._leases[0]
    moved = session.engine.transform([0, 2, 0, 0, 0, 0, 1, 1, 1])
    compare(session.engine, [collision.row(path, moved, [0, 0])], meshes, frames)
    compare(session.engine, [collision.row(path, IDENTITY, [1, 0])], meshes, frames)


def test_failed_scene_capture_releases_partial_world_and_recovers(session, assembly):
    rows, meshes, frames = fixture(session, assembly)
    compare(session.engine, rows, meshes, frames)
    invalid = list(frames[1])
    invalid[0] = float("nan")
    with pytest.raises(ValueError, match="transform"):
        collision.check(session.engine, rows, meshes, [frames[0], invalid])
    compare(session.engine, rows, meshes, frames)
    session.engine.clear_caches()
    compare(session.engine, rows, meshes, frames)
    assert session.engine.collision_checks.bytes <= 128 * 1024 * 1024
