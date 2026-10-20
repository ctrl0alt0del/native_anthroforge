"""Branch placement commits shared identity without moving the existing construction."""

import numpy as np
import pytest

from tests.test_junction_workflow import reference


def curve(session):
    return session.command(
        "curve.create",
        points=[dict(position=p) for p in ([0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0])],
        engine="POLYLINE",
    )


def branch(session, source, index=1):
    return session.command(
        "curve.branch.create",
        source=reference(session, source, index),
        points=[dict(position=[99, 99, 99]), dict(position=[2, index, 0])],
        engine="POLYLINE",
    )


def test_creation_is_one_undo_and_preserves_source_geometry(session):
    source = curve(session)
    session.wait()
    before, cursor = session.document.object(source), session.history.cursor
    child = branch(session, source)
    session.wait()
    assert session.history.cursor == cursor + 1
    assert session.document.object(child).points[0].position == before.points[1].position
    assert session.document.object(source).points[1].position == before.points[1].position
    assert len(session.document.junctions) == 1
    session.command("undo")
    assert child not in session.document.registry.records and not session.document.junctions
    session.command("redo")
    session.wait()
    assert session.document.object(child).result.status == "ready"


def test_reuse_existing_junction_and_atomic_edits(session):
    source = curve(session)
    one, two = branch(session, source), branch(session, source)
    session.wait()
    joint = session.document.object(one).points[0].junction
    assert session.document.object(two).points[0].junction == joint
    assert len(session.document.junctions) == 1
    session.command("curve.point.update", **reference(session, two), position=[0.3, 1, 0.5])
    session.wait()
    for key, index in ((source, 1), (one, 0), (two, 0)):
        np.testing.assert_allclose(
            session.document.object(key).points[index].position, [0.3, 1, 0.5]
        )


def test_invalid_source_leaves_no_curve_or_history(session):
    source = curve(session)
    before = session.document
    cursor = session.history.cursor
    with pytest.raises(ValueError, match="Unknown authored"):
        session.command(
            "curve.branch.create",
            source=dict(curve=source, point="missing"),
            points=[dict(position=[0, 0, 0]), dict(position=[1, 0, 0])],
        )
    assert session.document == before and session.history.cursor == cursor


def test_parented_source_root_uses_world_coordinates(session):
    source = curve(session)
    session.command("object.transform", target=source, values=[3, 4, 5, 0, 0, 0, 2, 2, 2])
    child = branch(session, source)
    session.wait()
    np.testing.assert_allclose(session.document.object(child).points[0].position, [3, 6, 5])
