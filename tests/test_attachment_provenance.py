"""Exact-input pose reuse never suppresses real edits, recapture or failures."""

from dataclasses import replace
from threading import Event
from unittest.mock import patch

from anthroforge.application import evaluation, projects
from anthroforge.core import attachment_provenance
from anthroforge.native import attachments


def test_unchanged_attachment_validation_and_reopen_keep_exact_pose(session, assembly, tmp_path):
    _, child = assembly
    before = session.document.entity(child)
    assert before.pose_receipt is not None
    target = tmp_path / "receipt.anthroforge"
    session.command("save", path=str(target), blocked_policy="wait")
    with patch.object(attachments, "apply_batch", wraps=attachments.apply_batch) as native:
        session.command("open", path=str(target))
        session.wait(10)
    native.assert_not_called()
    assert session.document.entity(child) == before
    assert session.document.revision == session.saved_revision


def test_tiny_parent_edit_is_not_rounded_away_and_undo_restores(session, assembly):
    root, child = assembly
    before = session.document.entity(child)
    session.command("scp.transform", entity=root, values=[1e-10, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait(10)
    after = session.document.entity(child)
    assert after.matrix[3] != before.matrix[3]
    assert after.pose_receipt != before.pose_receipt
    session.command("undo")
    session.wait(10)
    assert session.document.entity(child).matrix == before.matrix


def test_missing_provenance_performs_normal_startup_validation(session, assembly):
    _, child = assembly
    item = replace(session.document.entity(child), pose_receipt=None)
    session.replace_entities({child: item}, authored=False)
    with patch.object(attachments, "apply_batch", wraps=attachments.apply_batch) as native:
        projects.synchronize_loaded(session)
        session.wait(10)
    assert native.call_count >= 1
    assert session.document.entity(child).pose_receipt is not None


def test_binding_settings_and_failed_parent_invalidate_receipt(session, assembly):
    root, child = (session.document.entity(key) for key in assembly)
    assert not attachment_provenance.required([root, child], {child.id})
    changed = replace(child, attachment=replace(child.attachment, follow_rotation=False))
    assert attachment_provenance.required([root, changed], {child.id}) == {child.id}
    failed = replace(root, status="failed")
    assert attachment_provenance.required([failed, child], {child.id}) == {child.id}
    meshes = {key: asset.mesh for key, asset in session.assets.items()}
    result = attachments.propagate(session.engine, [failed, child], meshes, {child.id}, Event())
    assert result[-1].status == "failed"


def test_new_parent_geometry_and_explicit_recapture_are_evaluated(session, assembly):
    root, child = assembly
    parent, item = session.document.entity(root), session.document.entity(child)
    result = replace(parent.result, asset="new-geometry")
    assert attachment_provenance.required([replace(parent, result=result), item], {child})
    with patch.object(attachments, "apply_batch", wraps=attachments.apply_batch) as native:
        evaluation.request(session, {child}, {child})
        session.wait(10)
    assert native.call_count >= 1
