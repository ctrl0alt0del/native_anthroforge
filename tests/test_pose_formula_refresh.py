"""Pending pose work survives unchanged formula values after a sibling pose publishes."""

import numpy as np

from tests.conftest import CUBE
from tests.test_driving_formulas import reference
from tests.test_formula_geometry_barriers import scale_driver


def siblings(session, assembly):
    root, first = assembly
    second = session.command("import", path=str(CUBE), units=0.2, parent=root)["entity_id"]
    session.wait()
    session.command("scp.transform", entity=second, values=[-1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    scale_driver(session, second, reference(first, ("world_transform", "scale"), 0))
    session.wait()
    return root, first, second


def test_unchanged_formula_does_not_discard_pending_sibling_pose(session, assembly):
    root, first, second = siblings(session, assembly)
    before = session.document.entity(second).matrix
    move_with_queued_consumers(session, root)
    current = session.document.entity(second)
    assert current.status == "ready", [j.describe() for j in session.scheduler.jobs[-8:]]
    expected = np.array(before).reshape(4, 4)
    expected[1, 3] += 2
    np.testing.assert_allclose(np.array(current.matrix).reshape(4, 4), expected, atol=1e-10)
    session.command("undo")
    session.wait()
    session.command("redo")
    session.wait()
    np.testing.assert_allclose(session.document.entity(second).matrix, current.matrix, atol=1e-10)


def move_with_queued_consumers(session, root):
    session.scheduler.can_publish = lambda job: False
    session.command(
        "property.set", reference=reference(root, ("transform", "position"), 1), value=2
    )
    session.scheduler.can_publish = lambda job: True
    session.wait()
