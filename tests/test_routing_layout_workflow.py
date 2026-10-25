"""Adaptive path evaluation preserves authored preferences, history and consumer topology."""

import numpy as np
import pytest

from anthroforge.application import storage, surface_providers
from anthroforge.native import routing
from tests.conftest import CUBE
from tests.test_routing_layout import CASE, require_clear


def scene(session):
    session.command("preferences.set", routing_conversion_points="ALL_POINTS")
    parent = ""
    for surface in CASE["surfaces"]:
        parent = session.command("import", path=str(CUBE), units=1, parent=parent)["entity_id"]
        session.wait()
        session.command(
            "scp.transform", entity=parent, values=session.engine.decompose(surface["matrix"])
        )
        session.wait()
    key = session.command("curve.create", points=[dict(position=p) for p in CASE["points"]])
    session.wait()
    return key


def accepted(session, key):
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    targets = [item.id for item in session.document.entities[:2]]
    handles, matrices = surface_providers.inputs(
        session.engine, session.document, session.assets, targets
    )
    value = routing.Inputs(item, tuple(handles), tuple(matrices))
    path = session.resources.paths[item.result.asset].path
    require_clear(session, path, value)
    return path


def adaptive(session, key):
    session.command("curve.engine", curve=key, engine="ROUTED")
    session.wait()
    accepted(session, key)
    session.command("curve.engine_settings", curve=key, samples=4)
    session.wait()
    assert accepted(session, key).count > 4
    assert session.document.object(key).engine_settings.samples == 4


def test_direct_conversion_growth_undo_redo_and_roundtrip(session, tmp_path):
    key = scene(session)
    before = session.document.object(key).points
    adaptive(session, key)
    saved = tmp_path / "adaptive.anthroforge"
    session.command("save", path=str(saved), blocked_policy="wait")
    document, resources = storage.read_package(saved, session.engine)
    assert document.object(key).engine_settings.samples == 4
    assert resources.paths[document.object(key).result.asset].path.count > 4
    session.command("undo")
    assert session.document.object(key).engine_settings.samples == 64
    session.command("redo")
    session.wait()
    accepted(session, key)
    assert session.document.object(key).points == before


def test_adaptive_path_keeps_consumers_connectivity_and_attachment_locks(session):
    key = scene(session)
    adaptive(session, key)
    body, mesh = attached_consumer(session, key)
    point = session.document.object(key).points[1]
    position = [point.position[0] + 0.01, *point.position[1:]]
    session.command("curve.point.update", curve=key, point=point.id, position=position)
    session.wait()
    compare_consumer(session, body, mesh)
    accepted(session, key)


def attached_consumer(session, key):
    parent = session.document.entities[0].id
    body = session.command("primitive.from_curves", curves=[key], kind="BODY", parent=parent)
    session.wait()
    child = session.command("scp.empty", name="Attached child", parent=body)
    session.wait()
    mesh = session.assets[session.document.entity(body).result.asset].mesh
    with pytest.raises(ValueError, match=child):
        session.command("curve.engine_settings", curve=key, samples=8)
    return body, mesh


def compare_consumer(session, key, before):
    item = session.document.entity(key)
    assert item.result.status == "ready", item.result.error
    after = session.assets[item.result.asset].mesh
    for index in (1, 2, 3):
        np.testing.assert_array_equal(before.array(index), after.array(index))
