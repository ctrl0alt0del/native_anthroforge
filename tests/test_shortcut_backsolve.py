"""Native retained-anchor translation matches the addon's owner preservation semantics."""

from dataclasses import replace

import numpy as np

from anthroforge.core.entities import Attachment, SCP
from anthroforge.native import attachments, shortcut_attachments
from tests.conftest import CUBE


def pair(session, mode="FACE_CENTER"):
    mesh = session.engine.import_mesh(CUBE, 1.0, False)
    parent = SCP("Parent", asset="cube")
    child = SCP(
        "Owner",
        parent=parent.id,
        asset="cube",
        matrix=session.engine.transform([2, 0, 0, 0, 0, 20, 1, 1, 1]),
        attachment=Attachment(child_mode=mode),
    )
    return mesh, parent, attachments.capture(session.engine, child, parent, {"cube": mesh})


def test_backsolve_preserves_retained_anchor_with_translation_only(session):
    mesh, parent, child = pair(session)
    saved = shortcut_attachments.capture(session.engine, child, parent, {"cube": mesh})
    changed = replace(child, geometry_offset=(0.2, 0.1, -0.3))
    pose = shortcut_attachments.backsolve(session.engine, changed, parent, {"cube": mesh}, saved)
    solved = replace(changed, matrix=pose)
    final = shortcut_attachments.capture(session.engine, solved, parent, {"cube": mesh})
    np.testing.assert_allclose(final[-1], saved[-1], atol=1e-12)
    np.testing.assert_array_equal(
        np.array(pose).reshape(4, 4)[:3, :3], np.array(child.matrix).reshape(4, 4)[:3, :3]
    )


def test_backsolve_retains_parent_local_target_after_parent_motion(session):
    mesh, parent, child = pair(session, "OBJECT_ORIGIN")
    saved = shortcut_attachments.capture(session.engine, child, parent, {"cube": mesh})
    parent = replace(parent, matrix=session.engine.transform([0.3, -0.2, 0.7, 0, 0, 45, 1, 1, 1]))
    pose = shortcut_attachments.backsolve(session.engine, child, parent, {"cube": mesh}, saved)
    final = shortcut_attachments.capture(
        session.engine, replace(child, matrix=pose), parent, {"cube": mesh}
    )
    np.testing.assert_allclose(final[-1], saved[-1], atol=1e-12)


def test_invalidated_anchor_index_uses_retained_local_fallback(session):
    mesh, parent, child = pair(session)
    saved = shortcut_attachments.capture(session.engine, child, parent, {"cube": mesh})
    invalid = (saved[0], 1000000, saved[2], saved[3])
    pose = shortcut_attachments.backsolve(session.engine, child, parent, {"cube": mesh}, invalid)
    np.testing.assert_allclose(pose, child.matrix, atol=1e-12)
