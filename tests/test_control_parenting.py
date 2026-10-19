"""Ordinary control relationships share generic frames, workspaces and lifecycle."""

import numpy as np
import pytest

from anthroforge.application.control_frames import display_frame
from anthroforge.application.curve_sources import world
from tests.test_construction_contracts import create, hook, mesh


def move(session, command, target, x):
    field = {"object.transform": "target", "control.transform": "control"}.get(command, "entity")
    session.command(command, **{field: target, "values": [x, 0, 0, 0, 0, 0, 1, 1, 1]})
    session.wait()


def test_curve_parented_control_updates_geometry_and_detaches_without_jump(session):
    body = create(session)
    source = session.command("curve.create")
    control = hook(session, body)
    session.command("control.follow", control=control, entity=source)
    before = mesh(session, body).array(0).copy()
    move(session, "object.transform", source, 0.25)
    np.testing.assert_allclose(mesh(session, body).array(0), before + [0.25, 0, 0])
    frame = display_frame(session, session.document.control(control))
    session.command("object.delete", target=source)
    session.wait()
    np.testing.assert_allclose(display_frame(session, session.document.control(control)), frame)
    assert not session.document.control(control).follow and not session.scheduler.errors


def test_deleting_control_preserves_parented_curve_and_undo(session):
    control = session.command("control.create")
    source = session.command("curve.create", parent=control)
    move(session, "control.transform", control, 0.3)
    before = world(session.engine, session.document, source)
    session.command("control.delete", control=control)
    session.wait()
    assert not session.document.object(source).parent
    np.testing.assert_allclose(world(session.engine, session.document, source), before)
    session.command("undo")
    session.wait()
    assert session.document.object(source).parent == control and not session.scheduler.errors


def test_origin_relocation_preserves_child_curve_and_consumer(session, assembly):
    _, child = assembly
    source = session.command("curve.create", parent=child)
    body = session.command("primitive.from_curves", curves=[source], kind="BODY", parent=child)
    session.wait()
    frame, vertices = (
        world(session.engine, session.document, source),
        mesh(session, body).array(0).copy(),
    )
    session.command("scp.origin", entity=child)
    session.wait()
    np.testing.assert_allclose(world(session.engine, session.document, source), frame)
    np.testing.assert_allclose(mesh(session, body).array(0), vertices)
    assert not session.scheduler.errors


def test_controls_follow_consumers_into_workspaces_without_becoming_members(session):
    root = create(session)
    child = create(session, root)
    control = hook(session, child, session.command("control.create"))
    session.command("workspace.create", name="Child", members=[child])
    session.command("control.update", control=control, name="Accessible")
    assert control not in session.workspace.members
    with pytest.raises(ValueError, match="anatomical"):
        session.command("workspace.create", name="Invalid", members=[control])
