"""Reviewed recapture uses old support frames, then normal attachment propagation."""

from dataclasses import replace
from uuid import uuid4

import numpy as np
import pytest

from anthroforge.application.assets import Asset
from anthroforge.application.storage import write_package
from tests.test_anchor_operations import scene
from tests.test_mesh_replacement import tetrahedron
from tests.test_skeleton_update_commands import prepare, replacement
from tests.test_skeleton_update_controls import apply


def different_topology(session, bone, path):
    item = session.document.entity(bone)
    resource = session.engine.import_mesh(tetrahedron(path), 1, False)
    key, resources = str(uuid4()), session.resources.snapshot()
    resources.meshes[key] = Asset(resource, "test", "", 1, False)
    updated = replace(item, primitive=replace(item.primitive, source=key), asset=key)
    updated = replace(updated, result=replace(item.result, asset=key))
    values = tuple(updated if e.id == bone else e for e in session.document.entities)
    source = path / "changed.anthroforge"
    write_package(source, replace(session.document, entities=values), resources)
    return source


def test_topology_change_requires_review_and_preserves_support(session, tmp_path):
    bone, _, anchor = scene(session)
    path = different_topology(session, bone, tmp_path)
    state = prepare(session, path, {bone: bone})
    key = "rebind:" + anchor.id + ":" + bone
    assert not state["ready"] and any(r["key"] == key for r in state["findings"])
    state = prepare(session, path, {bone: bone}, rebind={key: True})
    assert state["ready"], state
    apply(session, state)
    updated = session.document.object(anchor.id)
    assert updated.binding.reference == anchor.binding.reference
    assert updated.result.status == "ready"


def correction(anchor, position):
    reference = anchor.binding.reference
    return {
        anchor.id: {
            anchor.id: dict(
                position=position,
                target=reference.target,
                role=reference.role,
                instance=reference.instance,
            )
        }
    }


def test_anchor_correction_is_captured_in_old_bone_frame(session, tmp_path):
    bone, _, anchor = scene(session)
    position, key = [2.25, 0.1, 0.5], "rebind:" + anchor.id + ":" + bone
    state = prepare(
        session,
        replacement(session, bone, tmp_path),
        {bone: bone},
        rebind={key: True},
        placements=correction(anchor, position),
    )
    assert state["ready"], state
    apply(session, state)
    np.testing.assert_allclose(session.document.object(anchor.id).resolved_position, position)
    session.wait()
    np.testing.assert_allclose(session.document.object(anchor.id).resolved_position, position)


def test_correction_cannot_silently_change_target_role(session, tmp_path):
    bone, _, anchor = scene(session)
    goals = correction(anchor, [2, 0, 0.5])
    goals[anchor.id][anchor.id]["role"] = "BASE"
    with pytest.raises(AssertionError, match="targets or roles"):
        prepare(
            session,
            replacement(session, bone, tmp_path),
            {bone: bone},
            rebind={"rebind:" + anchor.id + ":" + bone: True},
            placements=goals,
        )
