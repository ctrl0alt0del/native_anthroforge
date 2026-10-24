"""Complete symmetric source construction uses native geometry and ordinary undo."""

import numpy as np
import pytest


def curve(session, points, engine="BEZIER"):
    key = session.command("curve.create", points=[dict(position=p) for p in points], engine=engine)
    session.command("wait")
    return key


def path(session, key):
    return session.resources.paths[session.document.object(key).result.asset].path


@pytest.mark.parametrize("engine", ["BEZIER", "POLYLINE", "ROUTED"])
def test_symmetric_half_preserves_engine_knots_and_exact_sample_reflection(session, engine):
    key = curve(session, [(0, 0, 0), (1, 1, 0), (0, 2, 0)], engine)
    before, original = session.document.object(key), path(session, key)
    samples, count = original.array().copy(), original.count
    session.command("mirror.loop.create", curve=key)
    session.command("wait")
    item, result = session.document.object(key), path(session, key)
    assert item.result.status == "ready", item.result.error
    assert item.engine == engine and item.points == before.points
    assert result.closed and result.count == 2 * count - 2
    np.testing.assert_allclose(result.array()[:count, :3], samples[:, :3])
    np.testing.assert_allclose(result.array()[count:, :3], samples[-2:0:-1, :3] * [-1, 1, 1])
    session.command("undo")
    assert not session.document.object(key).closed


def test_invalid_half_does_not_move_points_or_add_undo(session):
    key = curve(session, [(0.2, 0, 0), (1, 1, 0), (0, 2, 0)])
    before, cursor = session.document.object(key), session.history.cursor
    with pytest.raises(ValueError, match="endpoints.*plane"):
        session.command("mirror.loop.create", curve=key)
    assert session.document.object(key) == before
    assert session.history.cursor == cursor


def surface(session, keys, **values):
    session.command("surface.create", curves=keys, **values)
    session.command("wait")
    return next(o for o in session.document.objects if hasattr(o, "mirror_order"))


def test_single_curve_mirrored_rows_build_one_surface(session):
    key = curve(session, [(1, 0, 0), (1, 0, 2)])
    item = surface(session, [key], mirrored_rows=True)
    assert item.mirror_order == (-1, 1)
    assert item.result.status == "ready", item.result.error
    mesh = session.assets[item.result.asset].mesh
    np.testing.assert_allclose([mesh.bounds[0], mesh.bounds[3]], [-1, 1])
    assert not any(v.source == item.id for v in session.document.mirrors.instances.values())


def test_mirrored_rows_direct_update_captures_order_and_material_layout(session):
    keys = [curve(session, [(x, 0, 0), (x, 0, 2)]) for x in (0.5, 1)]
    item = surface(session, keys)
    session.command("surface.update", target=item.id, mirrored_rows=True)
    session.command("wait")
    after = session.document.object(item.id)
    assert after.mirror_order == (-2, -1, 1, 2)
    assert len(after.across) == 3 and after.result.status == "ready", after.result.error
    session.command("undo")
    assert not session.document.object(item.id).mirrored_rows


def test_symmetric_definitions_roundtrip_without_recomputation(session, tmp_path):
    key = curve(session, [(0, 0, 0), (1, 1, 0), (0, 2, 0)])
    session.command("mirror.loop.create", curve=key)
    session.command("wait")
    before = path(session, key).array().copy()
    filename = str(tmp_path / "symmetric.anthroforge")
    session.command("save", path=filename, blocked_policy="wait")
    session.command("open", path=filename)
    np.testing.assert_array_equal(path(session, key).array(), before)
    assert session.document.object(key).symmetric is not None
