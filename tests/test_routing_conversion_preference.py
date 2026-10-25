"""Conversion preferences select guides without changing evaluation or binding policy."""

import json

import numpy as np
import pytest

from anthroforge.application.preferences import PreferenceStore
from tests.test_curve_conversion import source
from tests.test_fiber_creation import bind, scene
from tests.test_junction_workflow import reference
from tests.test_surface_workflow import surface


@pytest.mark.parametrize("mode", ["ENDPOINTS", "ALL_POINTS"])
@pytest.mark.parametrize("closed", [False, True])
def test_direct_switch_uses_preference_once_and_is_undoable(session, mode, closed):
    key = source(session, closed)
    before, cursor = session.document.object(key), session.history.cursor
    session.command("preferences.set", routing_conversion_points=mode)
    session.command("curve.engine", curve=key, engine="ROUTED")
    session.wait()
    after = session.document.object(key)
    expected = before.points if closed or mode == "ALL_POINTS" else before.points[::2]
    assert after.points == expected and after.result.status == "ready", after.result.error
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.object(key).points == before.points
    session.command("redo")
    session.wait()
    assert session.document.object(key).points == expected


def test_configured_switch_and_parametric_switch_use_the_same_default(session):
    a = source(session)
    b = session.command("curve.create", engine="PARAMETRIC", settings={"resolution": 9})
    session.wait()
    for key in (a, b):
        before = session.document.object(key)
        session.command("curve.engine", curve=key, engine="ROUTED", settings={"samples": 21})
        session.wait()
        item = session.document.object(key)
        assert item.result.status == "ready", item.result.error
        assert item.points == (before.points[0], before.points[-1])
        assert item.engine_settings.samples == 21


def test_default_fiber_conversion_preserves_captured_bindings_and_current_endpoints(session):
    target, original = scene(session)
    fiber = bind(session, target, original)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait()
    asset = session.resources.paths[session.document.object(fiber.id).result.asset]
    session.command("curve.engine", curve=fiber.id, engine="ROUTED")
    session.wait()
    after = session.document.object(fiber.id)
    assert after.result.status == "ready", after.result.error
    assert after.bindings == fiber.bindings
    assert tuple(p.id for p in after.points) == (fiber.points[0].id, fiber.points[-1].id)
    np.testing.assert_allclose([p.position for p in after.points], asset.path.array()[[0, -1], :3])


def test_interior_junction_remains_a_required_routing_point(session):
    a, b = source(session), source(session)
    point = session.document.object(a).points[1]
    joint = session.command(
        "junction.create", source={"curve": a, "point": point.id}, targets=[reference(session, b)]
    )
    session.wait()
    before = session.document.object(a)
    session.command("curve.engine", curve=a, engine="ROUTED")
    session.wait()
    after = session.document.object(a)
    assert after.result.status == "ready" and after.points == before.points
    assert after.points[1].junction == joint


def test_preference_does_not_modify_existing_routed_curves_or_history(session):
    key = source(session)
    session.command("preferences.set", routing_conversion_points="ALL_POINTS")
    session.command("curve.engine", curve=key, engine="ROUTED")
    session.wait()
    before, cursor = session.document, session.history.cursor
    session.command("preferences.set", routing_conversion_points="ENDPOINTS")
    session.command("curve.engine", curve=key, engine="ROUTED", settings={"accepted_steps": 2})
    session.wait()
    assert session.document.object(key).points == before.object(key).points
    assert session.history.cursor == cursor + 1


def test_legacy_preference_file_defaults_without_losing_solver_choice(tmp_path):
    path = tmp_path / "preferences.json"
    path.write_text(json.dumps({"schema": 1, "values": {"routing_backend": "PIQP"}}))
    store = PreferenceStore(path)
    assert store.value.routing_conversion_points == "ENDPOINTS"
    assert store.value.routing_backend == "PIQP" and not store.error
    store.update(routing_conversion_points="ALL_POINTS")
    assert PreferenceStore(path).value == store.value
    with pytest.raises(ValueError, match="ENDPOINTS or ALL_POINTS"):
        store.update(routing_conversion_points="UNKNOWN")
    assert PreferenceStore(path).value == store.value


def mapping(session, key):
    return [[p.id, i] for i, p in enumerate(session.document.object(key).points)]


def test_material_correspondence_is_retained_for_surviving_points_in_one_undo(session):
    a, key = aligned_surface(session)
    before, cursor = session.document.object(key), session.history.cursor
    session.command("curve.engine", curve=a, engine="ROUTED")
    session.wait()
    after = session.document.object(key)
    assert after.result.status == "ready", after.result.error
    assert after.alignment[0].stations == before.alignment[0].stations[::2]
    assert after.alignment[1] == before.alignment[1] and session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.object(key).alignment == before.alignment


def aligned_surface(session):
    a, b = source(session), source(session)
    key = surface(session, [a, b])
    session.command(
        "surface.correspondence",
        target=key,
        mapping={a: mapping(session, a), b: mapping(session, b)},
        across=[2],
    )
    session.wait()
    return a, key


def test_explicit_preview_points_override_default_and_all_points_mode_is_supported(session):
    key = source(session)
    before = session.document
    points = [p.id for p in before.object(key).points]
    for options in ({"points": points}, {}):
        if not options:
            session.command("preferences.set", routing_conversion_points="ALL_POINTS")
        session.command("curve.conversion.preview", curve=key, engine="ROUTED", **options)
        session.wait()
        assert session.conversion.state == "ready", session.conversion.error
        assert session.conversion.asset.authored.points == before.object(key).points
        assert session.document is before
        session.command("curve.conversion.cancel")
