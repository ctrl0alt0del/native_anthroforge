"""Standalone path edits use shared transactions, locks and inspection contracts."""

import json

import numpy as np
import pytest

from anthroforge.application.curve_sources import world
from tests.test_shared_curves import assembly


def test_polyline_subdivision_preserves_path_and_undo(session):
    key = session.command("curve.create", engine="POLYLINE")
    session.wait(5)
    curve = session.document.object(key)
    point = session.command("curve.subdivide", curve=key, segment=0, parameter=0.25)
    inserted = session.document.object(key).points[1]
    expected = np.array(curve.points[0].position) * 0.75 + np.array(curve.points[1].position) * 0.25
    assert inserted.id == point
    np.testing.assert_allclose(inserted.position, expected)
    session.command("undo")
    assert session.document.object(key).points == curve.points
    session.command("redo")
    assert session.document.object(key).points[1].id == point


def test_curve_inspection_describes_path_and_consumer_locks(session):
    _, curve, first, _ = assembly(session)
    child = session.command("scp.empty", name="Attachment", parent=first)
    session.wait(5)
    row = session.command("inspect.target", entity=curve)
    assert row["kind"] == "CURVE" and row["geometry"]["kind"] == "PATH"
    assert row["topology_locks"][0]["consumer"] == first
    assert row["topology_locks"][0]["id"] == child
    assert not row["attachment"]["bindings"]
    assert all(p["name"] != "Unavailable object" for r in row["relationships"] for p in r["inputs"])
    with pytest.raises(ValueError, match=child):
        session.command("curve.update", entity=first, curve=curve, resolution=32)
    json.dumps(session.command("inspect.snapshot"))


def test_world_transform_keeps_ordinary_parenting_distinct(session):
    parent = session.command("curve.create")
    session.command("object.transform", target=parent, values=[3, 2, 0, 0, 0, 45, 2, 1, 1])
    child = session.command("curve.create", parent=parent)
    values = [1, 0, 2, 0, 0, 10, 1, 1, 1]
    session.command("object.transform", target=child, values=values, world=True)
    np.testing.assert_allclose(
        world(session.engine, session.document, child), session.engine.transform(values), atol=1e-12
    )
    detail = session.command("inspect.target", entity=child)["attachment"]
    assert detail["transform_parent"] == parent and "support" not in detail
    session.command("workspace.update", hidden=[child], unpickable=[parent])
    assert child in session.workspace.hidden and parent in session.workspace.unpickable


def test_failed_closed_point_removal_is_atomic(session):
    key = session.command(
        "curve.create",
        engine="POLYLINE",
        closed=True,
        points=[dict(position=p) for p in ((0, 0, 0), (1, 0, 0), (0, 1, 0))],
    )
    before = session.document
    with pytest.raises(ValueError):
        session.command("curve.point.remove", curve=key, point=before.object(key).points[0].id)
    assert session.document == before
