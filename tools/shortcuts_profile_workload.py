"""Headless multi-output driver workload with accepted Parametric paths and a body."""

from math import pi
from time import perf_counter_ns

import numpy as np


def settings(points):
    return dict(
        x="r*cos(t)",
        y="r*sin(t)",
        z="0*m",
        resolution=points,
        interval=dict(end=2 * pi),
        variables=[dict(name="r", value=0.03, dimension="LENGTH", id="radius")],
    )


def create_curve(session, index, points):
    return session.command(
        "curve.create",
        name=f"Circle {index + 1}",
        engine="PARAMETRIC",
        closed=True,
        settings=settings(points),
    )


def fixture(session, outputs=12, points=256):
    curves = [create_curve(session, index, points) for index in range(outputs)]
    session.wait(30)
    driver = session.command("driver.create", value=0.03, dimension="LENGTH")
    for curve in curves:
        reference = dict(target=curve, path=["engine_settings", "variables", "@radius", "value"])
        session.command("driver.formula.add", driver=driver, target=reference, expression="value")
    body = session.command("primitive.from_curves", curves=[curves[0]], kind="BODY")
    session.wait(30)
    require_ready(session, curves, 0.03)
    return driver, curves, body


def require_ready(session, curves, radius):
    assert not session.scheduler.errors, session.scheduler.errors
    assert all(row.status == "ready" for row in session.document.formula_results)
    for key in curves:
        curve = session.document.object(key)
        resource = session.resources.paths[curve.result.asset]
        assert curve.result.status == "ready" and resource.path.closed
        points = resource.path.array()[:, :3]
        np.testing.assert_allclose(np.linalg.norm(points[:, :2], axis=1), radius, atol=1e-12)


def edits(session, driver, count):
    elapsed = []
    for index in range(count):
        start = perf_counter_ns()
        session.command("driver.value", driver=driver, value=0.031 + index * 0.0001)
        session.wait(30)
        elapsed.append((perf_counter_ns() - start) / 1e6)
    return elapsed, 0.031 + (count - 1) * 0.0001


def cache_state(session):
    cache = session.engine.expressions
    return dict(
        entries=len(cache.items),
        bytes=cache.bytes,
        entry_limit=cache.capacity,
        byte_limit=cache.budget,
    )


def workload(session, count=12):
    driver, curves, body = fixture(session)
    timings, radius = edits(session, driver, count)
    require_ready(session, curves, radius)
    assert session.document.entity(body).result.asset
    return dict(
        edit_ms=timings,
        outputs=len(curves),
        points_per_curve=256,
        dependent_bodies=1,
        expression_cache=cache_state(session),
    )
