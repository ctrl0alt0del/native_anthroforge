"""Native cursor projection, exact subdivision, stable identities and shared history."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.entities import IDENTITY
from anthroforge.native import curve_queries


def curved(mode="FREE", closed=False):
    points = (
        CurvePoint(position=(-1, 0, 0), right=(-0.5, 1, 0.2), radius=0.2, tilt=-0.5),
        CurvePoint(position=(1, 0, 0), left=(0.5, 1, -0.2), radius=1.2, tilt=1.5),
        CurvePoint(position=(1, -1, 1), left=(1.5, -0.5, 1), right=(0.5, -1.5, 0)),
    )
    return Curve(tuple(replace(p, left_mode=mode, right_mode=mode) for p in points), closed=closed)


def evaluate(cubic, parameters):
    t = np.asarray(parameters)[:, None]
    s = 1 - t
    return s**3 * cubic[0] + 3 * s * s * t * cubic[1] + 3 * s * t * t * cubic[2] + t**3 * cubic[3]


@pytest.mark.parametrize("mode", ["AUTO", "FREE", "ALIGNED", "VECTOR"])
@pytest.mark.parametrize("closed,segment", [(False, 0), (True, 2)])
def test_subdivision_preserves_entire_curve_and_ids(session, mode, closed, segment):
    curve = curved(mode, closed)
    changed = curve_queries.split(session.engine, curve, segment, 0.37)
    before = curve_queries.cubics(session.engine, curve, IDENTITY).reshape((-1, 4, 3))
    after = curve_queries.cubics(session.engine, changed, IDENTITY).reshape((-1, 4, 3))
    assert_shape(before, after, segment, 0.37)
    assert changed.id == curve.id
    assert [p.id for i, p in enumerate(changed.points) if i != segment + 1] == [
        p.id for p in curve.points
    ]
    a, b = curve.points[segment], curve.points[(segment + 1) % len(curve.points)]
    assert changed.points[segment + 1].radius == pytest.approx(0.63 * a.radius + 0.37 * b.radius)
    assert changed.points[segment + 1].tilt == pytest.approx(0.63 * a.tilt + 0.37 * b.tilt)


def assert_shape(before, after, segment, fraction):
    t = np.linspace(0, 1, 101)
    for index, cubic in enumerate(before):
        if index == segment:
            np.testing.assert_allclose(
                evaluate(cubic, t * fraction), evaluate(after[index], t), atol=1e-12
            )
            np.testing.assert_allclose(
                evaluate(cubic, fraction + t * (1 - fraction)),
                evaluate(after[index + 1], t),
                atol=1e-12,
            )
        else:
            np.testing.assert_allclose(cubic, after[index + (index > segment)], atol=1e-12)


@pytest.mark.parametrize("parameter", [0.001, 0.19, 0.51, 0.999])
def test_closest_cubic_matches_transformed_point(session, parameter):
    frame = session.engine.transform([2, -1, 3, 20, 15, 35, 2, 0.6, 1.3])
    curve = replace(curved(), matrix=session.engine.transform([0.4, 0, 0, 0, 0, 20, 1, 1, 1]))
    query = curve_queries.CurveQuery(session.engine, [curve], frame)
    point = evaluate(query.data.reshape((-1, 4, 3))[0], [parameter])[0]
    result = query.closest(point + [0, 0, 5], [0, 0, -1])
    assert result["curve"] == curve.id and result["segment"] == 0
    assert result["parameter"] == pytest.approx(parameter, abs=1e-7)
    np.testing.assert_allclose(result["position"], point, atol=1e-7)


def test_closest_curves_switch_and_reject_behind_camera(session):
    a, b = curved(), replace(curved(), matrix=session.engine.transform([3, 0, 0, 0, 0, 0, 1, 1, 1]))
    query = curve_queries.CurveQuery(session.engine, [a, b], IDENTITY)
    assert query.closest([-0.5, 0.5, 5], [0, 0, -1])["curve"] == a.id
    assert query.closest([2.5, 0.5, 5], [0, 0, -1])["curve"] == b.id
    assert not query.closest([0, 0, 5], [0, 0, 1])


@pytest.mark.parametrize(
    "segment,parameter", [(-1, 0.5), (2, 0.5), (0, 0), (0, 1), (0, float("nan"))]
)
def test_invalid_split_is_rejected(session, segment, parameter):
    with pytest.raises(ValueError, match="Subdivision"):
        curve_queries.split(session.engine, curved(), segment, parameter)


def test_split_command_keeps_attachment_topology_and_one_undo(session):
    entity = session.command("primitive.create", kind="LOFT")
    session.command("wait")
    session.command("scp.empty", name="Child", parent=entity)
    before = session.document.entity(entity)
    triangles = session.assets[before.asset].mesh.array(3).copy()
    cursor = session.history.cursor
    added = split_first(session, entity)
    session.command("wait")
    after = session.document.entity(entity)
    assert session.document.object(after.primitive.curves[0].id).points[1].id == added
    np.testing.assert_array_equal(session.assets[after.asset].mesh.array(3), triangles)
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.entity(entity).primitive == before.primitive


def split_first(session, entity):
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    return session.command("curve.split", entity=entity, curve=curve.id, segment=0, parameter=0.4)


def test_split_editable_parameters_roundtrip(session, tmp_path):
    entity = session.command("primitive.create", kind="BODY")
    point = split_first(session, entity)
    session.command("wait")
    before = session.document.entity(entity).primitive
    path = str(tmp_path / "split.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    assert session.document.entity(entity).primitive == before
    assert session.document.object(before.curves[0].id).points[1].id == point
