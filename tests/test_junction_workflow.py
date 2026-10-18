"""Shared authored points edit atomically and evaluate through accepted source provenance."""

import numpy as np
import pytest

from anthroforge.application.curve_sources import world
from tests.test_path_lifecycle import curve, path, point
from tests.test_shared_curves import move


def reference(session, key, index=0):
    return dict(curve=key, point=session.document.object(key).points[index].id)


def shared(session):
    a, b = curve(session), curve(session)
    move(session, b, 0.3)
    joint = session.command(
        "junction.create", source=reference(session, a), targets=[reference(session, b)]
    )
    session.wait()
    return a, b, joint


def position(session, key):
    return session.engine.world_point(
        world(session.engine, session.document, key), path(session, key)[0, :3]
    )


def test_join_has_no_wrapper_and_one_undo_and_preserves_explicit_identity(session):
    a, b, junction = shared(session)
    np.testing.assert_allclose(position(session, a), position(session, b))
    before = session.history.cursor
    record = session.command("junction.inspect", junction=junction)
    assert len(record["members"]) == 2 and session.history.cursor == before
    assert not session.document.entities
    session.command("undo")
    session.wait()
    assert not session.document.junctions
    session.command("redo")
    session.wait()
    assert session.document.junctions[0].id == junction
    np.testing.assert_allclose(position(session, a), position(session, b))


def test_editing_either_shared_point_updates_incident_authored_state_atomically(session):
    a, b, _ = shared(session)
    before = session.history.cursor
    point(session, b, [0.1, 0.4, 0])
    assert session.history.cursor == before + 1
    authored = [session.document.object(k).points[0].position for k in (a, b)]
    np.testing.assert_allclose(np.array(authored[0]), np.array(authored[1]) + [0.3, 0, 0])
    session.wait()
    np.testing.assert_allclose(position(session, a), position(session, b))
    session.command("undo")
    session.wait()
    np.testing.assert_allclose(position(session, a), position(session, b))
    assert not session.scheduler.errors


def test_source_transform_drives_follower_without_modifying_authored_points(session):
    a, b, _ = shared(session)
    before = session.document.object(b).points
    move(session, a, 0.2)
    np.testing.assert_allclose(position(session, a), position(session, b))
    assert session.document.object(b).points == before
    source = session.document.object(a).points
    move(session, b, 0.7)
    np.testing.assert_allclose(position(session, a), position(session, b))
    assert session.document.object(a).points == source


def test_junction_remove_preserves_current_shape_and_enables_deletion(session):
    a, b, joint = shared(session)
    move(session, a, 0.2)
    previous = path(session, b).copy()
    with pytest.raises(ValueError, match="Detach shared"):
        session.command("object.delete", target=a)
    session.command("junction.remove", junction=joint)
    session.wait()
    np.testing.assert_allclose(path(session, b), previous, atol=1e-12)
    session.command("object.delete", target=a)
    assert b in session.document.registry.records and not session.document.junctions


def test_manual_source_retains_accepted_shared_position_until_publication(session):
    a, b, _ = shared(session)
    before = position(session, b)
    session.command("update_mode", entity=a, mode="MANUAL")
    point(session, a, [-0.4, 0.5, 0])
    session.wait()
    np.testing.assert_allclose(position(session, b), before)
    assert a in session.document.object(b).result.pending
    session.command("curve.evaluate", curve=a)
    session.wait()
    np.testing.assert_allclose(position(session, a), position(session, b))
    assert not session.document.object(b).result.pending
