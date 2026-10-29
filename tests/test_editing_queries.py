"""Resolved reads share desktop state, retain revisions, and never author geometry."""

import numpy as np
import pytest

from anthroforge.application import editing_queries
from tests.test_fiber_editing import moved_fiber
from tests.test_fiber_interaction import controller as controller


def test_moved_fiber_matches_desktop_and_keeps_authored_state(controller):
    session = controller.session
    _, target = moved_fiber(session)
    controller.refresh()
    controller.select(target)
    controller.authoring.setEditing(True)
    before, cursor = session.document, session.history.cursor
    result = session.command("editing.inspect", target=target)
    rows = controller.authoring.rows
    assert [r["reference"] for r in result["components"]] == [r[0] for r in rows]
    np.testing.assert_array_equal([r["world"] for r in result["components"]], [r[1] for r in rows])
    assert result["components"][1]["local"][2] == pytest.approx(1.7)
    assert before.object(target).points[0].position[2] == pytest.approx(0.7)
    assert session.document is before and session.history.cursor == cursor


def test_paging_reuses_native_buffers_and_rejects_changed_inputs(session):
    _, target = moved_fiber(session)
    first = session.command("editing.inspect", target=target, limit=2)
    value = editing_queries.current(session, target)
    second = session.command(
        "editing.inspect", target=target, offset=2, expected_revision=first["revision"]
    )
    assert editing_queries.current(session, target) is value
    assert (
        first["components"] + second["components"]
        == session.command("editing.inspect", target=target)["components"]
    )
    session.command("object.rename", target=target, name="Changed")
    with pytest.raises(ValueError, match="inputs changed"):
        session.command("editing.inspect", target=target, expected_revision=first["revision"])


@pytest.mark.parametrize("offset,limit", [(-1, 1), (0, 0), (0, 16385), (True, 2)])
def test_page_limits_precede_geometry_resolution(session, offset, limit):
    with pytest.raises(ValueError):
        session.command("editing.inspect", target="absent", offset=offset, limit=limit)


def test_imported_members_are_read_only_and_keep_native_owner(session, assembly):
    root, _ = assembly
    value = editing_queries.current(session, root, "VERTEX")
    result = session.command("editing.inspect", target=root, category="VERTEX", limit=2)
    assert (
        value.buffers[0].owner
        is session.assets[session.document.entity(root).primitive.source].mesh
    )
    assert not value.buffers[0].world.flags.writeable
    assert all(not row["position_editable"] for row in result["components"])
    assert result["topology_locks"]
