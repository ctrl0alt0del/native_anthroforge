"""Generated knots preserve the existing Bezier sampling and consumer frames."""

from dataclasses import asdict, replace

import numpy as np

from anthroforge.application import storage
from anthroforge.core.parametric import Interval, ParametricSettings
from anthroforge.native import parametric, paths
from tests.test_fiber_creation import bind, path
from tests.test_parametric_consumers import imported
from tests.test_primitives import mesh


def parabola(session):
    points = [dict(position=[float(i), float(i * i), 0.0]) for i in range(3)]
    key = session.command("curve.create", points=points, settings=dict(resolution=7))
    session.wait(5)
    return key


def settings():
    return ParametricSettings(
        x="t*m",
        y="t*t*m",
        interval=Interval(end=2.0),
        resolution=3,
        interpolation="BEZIER",
        bezier_resolution=7,
    )


def test_native_generated_bezier_retains_positions_frames_and_parameters(session):
    key = parabola(session)
    source = session.document.object(key)
    before = paths.evaluate(session.engine, source)
    after, records = parametric.evaluate(
        session.engine, replace(source, engine_settings=settings())
    )
    np.testing.assert_array_equal(before.array(), after.array())
    np.testing.assert_array_equal(before.array(1), after.array(1))
    assert records.shape == (3, 13)


def convert(session, key):
    session.begin()
    session.command("curve.engine", curve=key, engine="PARAMETRIC", settings=asdict(settings()))
    session.commit()
    session.wait(5)


def hooked_body(session, key):
    body = session.command("primitive.from_curves", curves=[key], kind="BODY")
    session.wait(5)
    control = session.command("control.create", entity=body)
    session.command(
        "deformer.add", control=control, target=dict(owner=body, stage="CURVE", component=key)
    )
    session.command("control.transform", control=control, values=[0, 0, 0.25, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    return body


def test_body_and_hook_keep_shape_through_parametric_bezier_conversion(session):
    key = parabola(session)
    body = hooked_body(session, key)
    before = mesh(session, body).array(0).copy()
    convert(session, key)
    assert not session.scheduler.errors
    np.testing.assert_array_equal(mesh(session, body).array(0), before)
    session.command("curve.engine", curve=key, engine="BEZIER")
    session.wait(5)
    np.testing.assert_array_equal(mesh(session, body).array(0), before)
    assert storage.decode_document(storage.document_state(session.document)) == session.document


def test_fiber_preserves_bezier_path_and_sampling_then_follows_parent(session):
    parent, key = imported(session), parabola(session)
    convert(session, key)
    before = path(session, key)
    fiber = bind(session, parent, key)
    assert fiber.engine == "BEZIER" and fiber.resolution == 7
    np.testing.assert_array_equal(path(session, fiber.id), before)
    session.command("scp.transform", entity=parent, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    np.testing.assert_allclose(
        path(session, fiber.id)[:, :3], before[:, :3] + [0, 0, 1], atol=1e-12
    )
    np.testing.assert_array_equal(path(session, key), before)
