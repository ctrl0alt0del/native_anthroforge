"""Auto selects the body's flow capability; retained older bindings keep stable fallback."""

from dataclasses import replace
from threading import Event

import numpy as np

from anthroforge.application.shortcut_capture import snapshot
from anthroforge.core.construction import BodyPiece, Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.native.attachments import capture, packed_flags, propagate


def body_parent(parent):
    primitive = Primitive("BODY", curves=(CurveUse("guide"),), pieces=(BodyPiece("guide"),))
    return replace(parent, primitive=primitive)


def test_auto_capture_selects_flow_only_for_capable_parent(session, assembly):
    parent, child = map(session.document.entity, assembly)
    meshes = {key: asset.mesh for key, asset in session.assets.items()}
    stable = capture(session.engine, child, parent, meshes)
    assert stable.attachment.binding[6] == -1
    parent = body_parent(parent)
    auto = capture(session.engine, child, parent, meshes)
    explicit = replace(child, attachment=replace(child.attachment, strategy="DEFORMATION_FLOW"))
    explicit = capture(session.engine, explicit, parent, meshes)
    assert auto.attachment.binding[6] >= 0
    assert auto.attachment.binding == explicit.attachment.binding
    assert packed_flags([parent, auto], {child.id})["flows"].tolist() == [0, 1]
    assert snapshot(parent).primitive == parent.primitive


def test_legacy_auto_binding_keeps_stable_fallback_without_recapture(session, assembly):
    parent, child = map(session.document.entity, assembly)
    meshes = {key: asset.mesh for key, asset in session.assets.items()}
    parent = body_parent(parent)
    child = replace(child, pose_receipt=None)
    assert child.attachment.binding[6] == -1
    stable = replace(child, attachment=replace(child.attachment, strategy="STABLE_SURFACE"))
    auto_result = propagate(session.engine, [parent, child], meshes, {child.id}, Event())[1]
    stable_result = propagate(session.engine, [parent, stable], meshes, {child.id}, Event())[1]
    np.testing.assert_array_equal(auto_result.matrix, stable_result.matrix)
    assert auto_result.attachment == child.attachment
