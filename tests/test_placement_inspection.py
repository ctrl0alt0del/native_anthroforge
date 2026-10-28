"""Diagnostic placement reuses the exact preview/confirmed queries and preserves bindings."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection_placement, surface_queries
from tests.test_fiber_creation import bind, scene
from tests.test_surface_query_modes import capture, compound, material_point


def test_nearest_evidence_exposes_excluded_inner_shell(session):
    mesh = compound(session.engine)
    before = mesh.array(0).copy()
    preview = surface_queries.prepare(mesh, None, surface_queries.Mode.PREVIEW)
    confirmed = surface_queries.prepare(mesh, None, surface_queries.Mode.CONFIRMED)
    raw, clean = inspect_nearest(session, preview), inspect_nearest(session, confirmed)
    assert raw["candidates"][0]["distance"] == pytest.approx(0.15)
    assert clean["candidates"][0]["distance"] == pytest.approx(0.4)
    binding = capture(confirmed, [0.1, 0, 0])[1][0]
    np.testing.assert_allclose(clean["candidates"][0]["position"], material_point(mesh, binding))
    np.testing.assert_array_equal(mesh.array(0), before)


def inspect_nearest(session, query):
    return inspection_placement.inspect(
        session.engine, [query.mesh.handle], [IDENTITY], [0.1, 0, 0, 0, 0, 0, 0], False, 0
    )


def test_ray_inspection_preserves_document_and_binding(session):
    target, curve = scene(session)
    fiber = bind(session, target, curve)
    before, history = session.document, session.history.cursor
    result = inspect_ray(session, target, curve)
    assert result["state"] == "ready", result
    report = result["report"]
    assert report["confirmed"]["approach_cosine"] == pytest.approx(-1)
    assert report["displacement"][3] == pytest.approx(0)
    assert session.document is before and session.history.cursor == history
    assert session.document.object(fiber.id).bindings == fiber.bindings


def inspect_ray(session, target, curve):
    session.command(
        "geometry.placement",
        target=curve,
        targets=[target],
        position=[0, 0, 2],
        direction=[0, 0, -1],
    )
    session.wait()
    return session.command("geometry.placement.status")


def test_bound_point_report_uses_existing_support_and_retains_offsets(session):
    target, curve = scene(session)
    fiber = bind(session, target, curve)
    before = session.document
    session.command("geometry.binding", target=fiber.id, point=fiber.bindings[0].point)
    session.wait()
    result = session.command("geometry.binding.status")
    assert result["state"] == "ready", result
    report = result["report"]
    assert report["confirmed"]["reference"]["target"] == target
    assert report["support_distance"] == pytest.approx(0.2, abs=1e-6)
    assert session.document is before
