"""Frozen surface witnesses, presentation history and persisted camera contracts."""

import pytest

from tests.test_construction_contracts import create


def test_native_world_coordinates_and_distance_use_canonical_metres(session):
    from anthroforge.native.measurement import distance

    entity = create(session)
    original = endpoints(session, entity)[0]["position"]
    session.command("scp.transform", entity=entity, values=[2, 3, 4, 0, 0, 0, 2, 3, 4])
    point = endpoints(session, entity)[0]["position"]
    expected = [
        value * scale + offset
        for value, scale, offset in zip(original, (2, 3, 4), (2, 3, 4), strict=True)
    ]
    assert point == pytest.approx(expected)
    assert distance(session.engine, [1, 2, 3], [4, 6, 3]) == pytest.approx([3, 4, 0, 5])


def endpoints(session, entity):
    return [
        session.command("measurement.point", entity=entity, triangle=0, weights=w)
        for w in ([1, 0, 0], [0, 1, 0])
    ]


def test_measurement_uses_world_frame_and_stays_frozen_when_surface_moves(session):
    entity = create(session)
    session.command("scp.transform", entity=entity, values=[2, 3, 4, 15, 25, 35, 2, 3, 4])
    first, second = endpoints(session, entity)
    cursor = session.history.cursor
    session.command("measurement.add", start=first, end=second)
    row = session.command("measurement.list")[0]
    assert row["distance"] > 0 and not row["stale"]
    assert session.history.cursor == cursor
    session.command("scp.transform", entity=entity, values=[3, 3, 4, 15, 25, 35, 2, 3, 4])
    changed = session.command("measurement.list")[0]
    assert changed["stale"] and changed["distance"] == row["distance"]
    assert changed["start"]["position"] == first["position"]
    session.command("undo")
    assert not session.command("measurement.list")[0]["stale"]


def test_measurement_survives_deleted_geometry_without_retaining_its_asset(session):
    entity = create(session)
    a, b = endpoints(session, entity)
    session.command("measurement.add", start=a, end=b)
    session.command("scp.delete", entity=entity)
    row = session.command("measurement.list")[0]
    assert row["stale"] and row["start"]["name"] == "Deleted SCP"
    session.command("measurement.remove", measurement=row["id"])
    assert not session.command("measurement.list")


def test_bookmark_restores_exact_camera_during_edit_without_committing(session):
    entity = create(session)
    camera = [1, 2, 3, 4, 5, 6, 7]
    session.command("workspace.update", camera=camera, orthographic=True)
    identity = session.command("bookmark.add", name="Side")
    session.command("begin")
    session.command("scp.rename", entity=entity, name="Editing")
    session.command("workspace.update", camera=[0, 0, 0, 0, 0, 0, 10], orthographic=False)
    session.command("bookmark.restore", bookmark=identity)
    assert session.workspace.camera == tuple(camera) and session.workspace.orthographic
    assert session.history.before is not None
    session.command("cancel")
    assert session.workspace.bookmarks[0].id == identity
    assert session.workspace.camera == tuple(camera)


def test_annotations_round_trip_and_units_do_not_change_coordinates(session, tmp_path):
    entity = create(session)
    a, b = endpoints(session, entity)
    session.command("measurement.add", start=a, end=b, name="Width")
    session.command("bookmark.add", name="Comparison")
    session.command("workspace.update", display_units="mm")
    original = session.workspace
    path = str(tmp_path / "inspection.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.wait(10)
    session.command("open", path=path)
    assert session.workspace == original
    assert session.command("measurement.list")[0]["start"]["position"] == a["position"]


def test_invalid_surface_witness_and_blocked_annotation_edits(session):
    entity = create(session)
    with pytest.raises(ValueError):
        session.command("measurement.point", entity=entity, triangle=999999, weights=[1, 0, 0])
    with pytest.raises(ValueError):
        session.command("measurement.point", entity=entity, triangle=0, weights=[1, 1, 0])
    session.waiting_save = True
    with pytest.raises(ValueError, match="saving"):
        session.command("bookmark.add", name="Blocked")
    session.waiting_save = False


def test_displayed_geometry_retains_its_witness_identity_when_replacement_is_staged():
    from anthroforge.desktop.models import presentation

    previous = dict(
        active=True, key="old:0", handle=4, chunk=0, geometry_asset="old", geometry_revision=3
    )
    current = dict(key="new:0", handle=5, chunk=0, geometry_asset="new", geometry_revision=4)
    visible = presentation(previous, current)
    assert visible["handle"] == 4 and visible["geometry_asset"] == "old"
    assert visible["geometry_revision"] == 3
