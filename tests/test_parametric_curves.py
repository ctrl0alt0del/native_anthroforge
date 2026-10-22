"""Parametric equations share accepted paths, consumers and native geometry contracts."""

from math import pi

import numpy as np
import pytest

from anthroforge.application import storage


def create(session, **settings):
    key = session.command("curve.create", engine="PARAMETRIC", settings=settings)
    session.wait(5)
    assert not session.scheduler.errors
    return key


def positions(session, key):
    item = session.document.object(key)
    return session.resources.paths[item.result.asset].path.array()[:, :3].copy()


def circle_settings():
    return dict(
        x="r*cos(t)",
        y="r*sin(t)",
        z="0",
        resolution=17,
        interval=dict(start=0.0, end=2 * pi),
        variables=[dict(name="r", dimension="LENGTH", value=0.3)],
    )


def test_uniform_parameter_sampling_and_implicit_typed_variables(session):
    key = create(session, **circle_settings())
    item = session.document.object(key)
    angle = np.linspace(0, 2 * pi, 17)
    np.testing.assert_allclose(positions(session, key)[:, 0], 0.3 * np.cos(angle), atol=1e-14)
    np.testing.assert_allclose(positions(session, key)[:, 1], 0.3 * np.sin(angle), atol=1e-14)
    variable = item.engine_settings.variables[0]
    ref = dict(target=key, path=["engine_settings", "variables", "@" + variable.id, "value"])
    assert session.command("property.get", reference=ref)["dimension"] == "LENGTH"
    session.command("shortcut.set", reference=ref, value=0.5)
    session.wait(5)
    assert positions(session, key)[0, 0] == 0.5
    assert len(session.document.object(key).points) == 17


def test_closed_sampling_has_no_duplicate_seam_and_allows_straight_closure(session):
    key = session.command(
        "curve.create", engine="PARAMETRIC", closed=True, settings=circle_settings()
    )
    session.wait(5)
    points = positions(session, key)
    assert len(points) == 17
    assert not np.allclose(points[0], points[-1])
    session.command("curve.parametric.configure", curve=key, changes=dict(interval=dict(end=pi)))
    session.wait(5)
    assert session.resources.paths[session.document.object(key).result.asset].path.closed
    assert len(positions(session, key)) == 17


@pytest.mark.parametrize("engine", ["BEZIER", "POLYLINE"])
def test_direct_engine_switch_retains_points_and_stored_definition(session, engine):
    key = create(session, **circle_settings())
    before, old = positions(session, key), session.document.object(key)
    session.command("curve.engine", curve=key, engine=engine)
    session.wait(5)
    np.testing.assert_allclose(positions(session, key), before, atol=1e-14)
    assert session.document.object(key).parametric_definition == old.engine_settings
    session.command("curve.engine", curve=key, engine="PARAMETRIC")
    session.wait(5)
    np.testing.assert_allclose(positions(session, key), before, atol=1e-14)
    assert storage.decode_document(storage.document_state(session.document)) == session.document


def test_invalid_equation_retains_accepted_path_then_recovers(session):
    key = create(session)
    old = session.document.object(key).result.asset
    session.command("curve.parametric.configure", curve=key, changes=dict(x="1/0"))
    session.wait(5)
    assert session.document.object(key).result.asset == old
    assert session.document.object(key).result.status == "failed"
    session.command("curve.parametric.configure", curve=key, changes=dict(x="t*m"))
    session.wait(5)
    assert session.document.object(key).result.status == "ready"


def test_generated_coordinates_are_read_only_through_api_and_wrappers(session):
    key = create(session)
    point = session.document.object(key).points[0]
    ref = dict(target=key, path=["points", "@" + point.id, "position"])
    assert not session.command("property.get", reference=ref)["writable"]
    with pytest.raises(ValueError, match="controlled"):
        session.command("property.set", reference=ref, value=[1.0, 0.0, 0.0])
    with pytest.raises(ValueError, match="controlled"):
        session.command("curve.point.insert", curve=key, index=1, point=dict(position=[1, 1, 1]))


def test_interval_expressions_and_integer_variables(session):
    key = create(
        session,
        interval=dict(end_expression="n/2"),
        variables=[dict(name="n", value=8, numeric_type="INTEGER")],
        resolution=5,
    )
    np.testing.assert_allclose(positions(session, key)[:, 0], [0, 1, 2, 3, 4])
    ref = dict(target=key, path=["engine_settings", "interval", "end"])
    assert not session.command("property.get", reference=ref)["writable"]
