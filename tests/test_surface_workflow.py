"""Curve-only surfaces use the shared writer, authored job, persistence and undo contracts."""

import numpy as np
import pytest

from anthroforge.core.surfaces import Surface


def curve(session, y=0, closed=False):
    points = (
        [[0, y, 0], [1, y, 0], [1, y + 0.3, 0], [0, y + 0.3, 0]]
        if closed
        else [[0, y, 0], [1, y, 0]]
    )
    key = session.command(
        "curve.create", points=[dict(position=p) for p in points], engine="POLYLINE", closed=closed
    )
    session.wait()
    return key


def surface(session, sources, kind="LOFT", **options):
    session.command("surface.create", curves=sources, kind=kind, **options)
    session.wait()
    found = [o for o in session.document.objects if isinstance(o, Surface)]
    assert found, session.scheduler.errors
    return found[-1].id


def vertices(session, target):
    item = session.document.object(target)
    assert item.result.status == "ready", item.result.error
    return session.assets[item.result.asset].mesh.array(0).copy()


def test_surface_creates_without_anatomy_and_has_one_undo(session):
    a, b = curve(session), curve(session, 0.4)
    before = session.history.cursor
    key = surface(session, [a, b])
    assert not session.document.entities and session.history.cursor == before + 1
    assert len(vertices(session, key)) >= 4
    session.command("undo")
    assert key not in session.document.registry.records
    assert {a, b}.issubset(session.document.registry.records)
    session.command("redo")
    session.wait()
    assert len(vertices(session, key)) >= 4


def test_surface_source_edit_updates_live_mesh_and_deletion_preserves_curves(session):
    a, b = curve(session), curve(session, 0.4)
    key = surface(session, [a, b])
    before = vertices(session, key)
    point = session.document.object(a).points[0].id
    session.command("curve.point.update", curve=a, point=point, position=[0, 0, 0.2])
    session.wait()
    assert not np.array_equal(before, vertices(session, key))
    with pytest.raises(ValueError, match="referenced"):
        session.command("object.delete", target=a)
    session.command("object.delete", target=key)
    assert {a, b}.issubset(session.document.registry.records)


def test_surface_manual_and_on_release_keep_accepted_geometry(session):
    a, b = curve(session), curve(session, 0.4)
    key = surface(session, [a, b])
    original = session.document.object(key).result.asset
    session.command("update_mode", entity=key, mode="ON_RELEASE")
    session.command("begin")
    session.command("surface.update", target=key, flip=True)
    session.wait()
    assert session.document.object(key).result.asset == original
    session.command("commit")
    session.wait()
    assert session.document.object(key).result.asset != original
    manual_update(session, key)


def manual_update(session, key):
    session.command("update_mode", entity=key, mode="MANUAL")
    original = session.document.object(key).result.asset
    session.command("surface.update", target=key, flip=False)
    session.wait()
    assert session.document.object(key).result.asset == original
    session.command("evaluate", entities=[key])
    session.wait()
    assert session.document.object(key).result.asset != original


def test_patch_layout_and_asset_roundtrip_without_rerouting_on_open(session, tmp_path):
    source = curve(session, closed=True)
    key = surface(session, [source], "PATCH")
    before, definition = vertices(session, key), session.document.object(key)
    path = str(tmp_path / "surface.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    assert session.document.object(key) == definition
    np.testing.assert_allclose(vertices(session, key), before)
    assert not any(j.active and key in j.outputs for j in session.scheduler.jobs)


def test_surface_conversion_modes_switch_without_a_jump(session):
    a, b = curve(session), curve(session, 0.4)
    key = surface(session, [a, b])
    before = vertices(session, key)
    session.command("surface.source", target=key, curve=a, mode="SHAPE_ONLY")
    session.wait()
    np.testing.assert_allclose(vertices(session, key), before)
    session.command("object.transform", target=a, values=[0, 0, 0.3, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(vertices(session, key), before)
    session.command("surface.source", target=key, curve=a, mode="SHAPE_AND_TRANSFORM")
    session.wait()
    np.testing.assert_allclose(vertices(session, key), before)
