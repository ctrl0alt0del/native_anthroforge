"""Automatic scene membership is shared by previews, jobs, persistence and undo."""

from pathlib import Path

import pytest

from anthroforge.application import dependencies, storage
from anthroforge.core.results import Port
from anthroforge.core.routing_obstacles import targets

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"
LINE = [dict(position=(-2, 0, 0)), dict(position=(2, 0, 0))]


def curve(session, owner=""):
    key = session.command(
        "curve.create",
        engine="ROUTED",
        owner=owner,
        points=[
            dict(position=(-2, 0, 0)),
            dict(position=(2, 0, 0)),
        ],
    )
    session.wait(10)
    return key


def cube(session, parent="", y=0):
    key = session.command("import", path=str(CUBE), units=1, parent=parent)["entity_id"]
    session.wait(10)
    session.command("scp.transform", entity=key, values=[0, y, 0, 0, 0, 0, 1, 1, 1])
    session.wait(10)
    return key


def ready(session, key):
    session.wait(10)
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    return item


def test_new_obstacle_is_discovered_and_removal_undo_restores_membership(session):
    key = curve(session)
    before = ready(session, key)
    root = cube(session)
    item = ready(session, key)
    assert targets(session.document, item) == (root,) and not item.engine_settings.obstacles
    assert item.result.asset != before.result.asset
    session.command("scp.delete", entity=root)
    assert not targets(session.document, ready(session, key))
    session.command("undo")
    assert targets(session.document, ready(session, key)) == (root,)


def test_moving_previously_distant_surface_recomputes_path(session):
    root = cube(session, y=3)
    key = curve(session)
    before = ready(session, key)
    session.command("scp.transform", entity=root, values=[0, 0, 0, 0, 0, 0, 1, 1, 1])
    after = ready(session, key)
    assert after.result.asset != before.result.asset
    assert Port(root, "pose") in dependencies.ports(session.document, Port(key, "path"))


def test_exclusions_roundtrip_and_deleting_excluded_surface_is_allowed(session, tmp_path):
    root = cube(session)
    key = curve(session)
    session.command("curve.engine_settings", curve=key, excluded_obstacles=[root])
    item = ready(session, key)
    assert not targets(session.document, item)
    path = tmp_path / "excluded.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    document, _ = storage.read_package(path, session.engine)
    assert document.object(key).engine_settings == item.engine_settings
    assert document.object(key).result.inputs == item.result.inputs
    session.command("scp.delete", entity=root)
    assert not ready(session, key).engine_settings.excluded_obstacles


def test_consumer_is_excluded_automatically_but_explicit_cycle_remains_an_issue(session):
    key = curve(session)
    consumer = session.command("primitive.from_curves", curves=[key], kind="BODY")
    item = ready(session, key)
    graph = dependencies.graph(session.document)
    assert consumer in graph.routing_excluded[key] and not graph.blocked
    assert consumer not in targets(session.document, item)
    session.command("curve.engine_settings", curve=key, obstacles=[consumer])
    session.wait(10)
    assert Port(key, "path") in dependencies.blocked(dependencies.graph(session.document))
    assert session.document.object(key).result.asset == item.result.asset


def test_automatic_conversion_preview_becomes_stale_when_new_surface_appears(session):
    key = session.command("curve.create", points=LINE)
    session.wait(10)
    result = session.command("curve.conversion.preview", curve=key, engine="ROUTED")
    session.wait(10)
    assert session.conversion.state == "ready"
    cube(session)
    assert session.command("curve.conversion.status")["state"] == "stale"
    with pytest.raises(ValueError, match="current successful"):
        session.command("curve.conversion.accept", token=result["token"])
