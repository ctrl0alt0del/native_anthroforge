"""Source-linked instances preserve geometry and shared relationships across history."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import surface_providers
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.mirroring import MirrorInstance, MirrorRule
from anthroforge.core.surface_references import SurfaceReference
from tests.conftest import CUBE


def hierarchy():
    root = SCP("Root", id="root")
    child = SCP("Child", id="child", parent="root")
    tip = SCP("Tip", id="tip", parent="child")
    return Document(entities=(root, child, tip), mirror_rules=(MirrorRule("root", enabled=True),))


def test_inheritance_opt_out_nested_rules_and_stable_plane_identity():
    document = hierarchy()
    assert set(document.mirrors.instances) == {"mirror/root/child", "mirror/root/tip"}
    nested = replace(document, mirror_rules=(*document.mirror_rules, MirrorRule("child", True)))
    assert set(nested.mirrors.instances) == {"mirror/child/tip"}
    excluded = replace(
        document, mirror_rules=(*document.mirror_rules, MirrorRule("child", inherit=False))
    )
    assert not excluded.mirrors.instances
    moved = replace(document, mirror_rules=(MirrorRule("root", True, shift=3),))
    assert moved.mirrors.instances.keys() == document.mirrors.instances.keys()


@pytest.mark.parametrize("axis,index", [("X", 0), ("Y", 1), ("Z", 2)])
def test_reflection_plane_and_involution(axis, index):
    matrix = np.array(MirrorRule("root", axis=axis, shift=2).frame).reshape(4, 4)
    point = np.array([1.0, 2.0, 3.0, 1.0])
    expected = point.copy()
    expected[index] = 4 - point[index]
    np.testing.assert_array_equal(matrix @ point, expected)
    np.testing.assert_array_equal(matrix @ matrix, np.eye(4))
    assert np.linalg.det(matrix) == -1


def test_instances_share_native_assets_and_preserve_source_results(session, assembly):
    root, child = assembly
    before = session.document.entity(child)
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    ref = SurfaceReference(child, instance=root)
    original = surface_providers.get(session.engine, session.document, session.assets, child)
    reflected = surface_providers.get(session.engine, session.document, session.assets, ref)
    assert reflected.resource is original.resource
    assert session.document.entity(child) is before
    np.testing.assert_allclose(
        np.array(reflected.frame).reshape(4, 4),
        np.array(session.document.mirrors.rules[root].frame).reshape(4, 4)
        @ np.array(original.frame).reshape(4, 4),
    )
    assert session.command("mirror.source", target=MirrorInstance(child, root).id) == child


def test_mirror_mutation_rejected_and_history_restores_rule(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True)
    identity = MirrorInstance(child, root).id
    with pytest.raises(ValueError, match="read-only"):
        session.command("scp.rename", entity=identity, name="Wrong")
    session.command("undo")
    assert not session.command("mirror.list")
    session.command("redo")
    assert session.command("mirror.list")[0]["id"] == identity


def test_mirror_metadata_roundtrip_without_extra_geometry(session, assembly, tmp_path):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True)
    assets = set(session.assets)
    path = str(tmp_path / "mirrored.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    assert session.command("mirror.list")[0]["source"] == child
    assert set(session.assets) == assets


def test_result_publication_reuses_mirror_relationship_index():
    document = hierarchy()
    source = replace(document.entity("child"), result_generation=42)
    changed = replace(document, entities=(document.entity("root"), source, document.entity("tip")))
    assert changed.mirrors is document.mirrors


def test_anchor_captures_mirror_and_blocks_removal(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    identity = MirrorInstance(child, root).id
    point = session.command("construction.point.create", position=[3, 0, 0])
    result = session.command("anchor.create", source=point, parent=identity)
    session.command("wait")
    anchor = session.document.object(result["object_id"])
    assert anchor.binding.reference == SurfaceReference(child, instance=root)
    blockers = session.command("mirror.removal.inspect", target=root, enabled=False)
    assert any(row["id"] == anchor.id for row in blockers)
    with pytest.raises(ValueError, match="referenced consumers"):
        session.command("mirror.configure", target=root, enabled=False)
    assert identity in session.document.mirrors.instances


def test_plane_change_updates_bound_anchor_without_rebinding(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    point = session.command("construction.point.create", position=[3, 0, 0])
    result = session.command("anchor.create", source=point, parent=MirrorInstance(child, root).id)
    session.command("wait")
    before = session.document.object(result["object_id"])
    session.command("mirror.configure", target=root, shift=3)
    session.command("wait")
    after = session.document.object(before.id)
    assert after.binding == before.binding
    np.testing.assert_allclose(
        np.array(after.resolved_position) - before.resolved_position, [2, 0, 0]
    )


def test_routed_source_automatically_avoids_reflected_obstacle(session):
    from tests.conftest import CUBE

    root = session.command("scp.empty", name="Root")
    bone = session.command("import", path=str(CUBE), units=.5, parent=root)["entity_id"]
    session.command("wait")
    session.command("scp.transform", entity=bone, values=[2, 0, 0, 0, 0, 0, 1, 1, 1])
    key = session.command("curve.create", engine="ROUTED", points=[dict(position=p) for p in [(-2, 0, -2), (-2, 0, 2)]])
    session.command("wait")
    session.command("mirror.configure", target=root, enabled=True)
    session.command("wait")
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    samples = session.resources.paths[item.result.asset].path.array()[:, :2]
    assert np.max(np.linalg.norm(samples - [-2, 0], axis=1)) > .2


def test_scp_mirrored_parent_tracks_plane_without_rebinding(session, assembly):
    root, parent = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    child = session.command("import", path=str(CUBE), units=.05, parent=parent)["entity_id"]
    session.command("wait")
    session.command("scp.reparent", entity=child, parent=MirrorInstance(parent, root).id)
    session.command("wait")
    before = session.document.entity(child)
    assert before.status == "ready", before.error
    session.command("mirror.configure", target=root, shift=3)
    session.command("wait")
    after = session.document.entity(child)
    assert after.status == "ready" and after.attachment == before.attachment, after.error
    np.testing.assert_allclose(np.array(after.matrix)[[3, 7, 11]] - np.array(before.matrix)[[3, 7, 11]], [2, 0, 0], atol=1e-10)
