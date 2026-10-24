"""Source-linked instances preserve geometry and shared relationships across history."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import surface_providers
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.mirroring import MirrorInstance, MirrorRule
from anthroforge.core.surface_references import SurfaceReference


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
    excluded = replace(document, mirror_rules=(*document.mirror_rules, MirrorRule("child", inherit=False)))
    assert not excluded.mirrors.instances
    moved = replace(document, mirror_rules=(MirrorRule("root", True, shift=3),))
    assert moved.mirrors.instances.keys() == document.mirrors.instances.keys()


@pytest.mark.parametrize("axis,index", [("X", 0), ("Y", 1), ("Z", 2)])
def test_reflection_plane_and_involution(axis, index):
    matrix = np.array(MirrorRule("root", axis=axis, shift=2).frame).reshape(4, 4)
    point = np.array([1., 2., 3., 1.])
    expected = point.copy()
    expected[index] = 4 - point[index]
    np.testing.assert_array_equal(matrix @ point, expected)
    np.testing.assert_array_equal(matrix @ matrix, np.eye(4))
    assert np.linalg.det(matrix) == -1


def test_instances_share_native_assets_and_preserve_source_results(session, assembly):
    root, child = assembly
    before = session.document.entity(child)
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    identity = MirrorInstance(child, root).id
    ref = SurfaceReference(child, instance=root)
    original = surface_providers.get(session.engine, session.document, session.assets, child)
    reflected = surface_providers.get(session.engine, session.document, session.assets, ref)
    assert reflected.resource is original.resource
    assert session.document.entity(child) is before
    np.testing.assert_allclose(np.array(reflected.frame).reshape(4, 4),
                               np.array(session.document.mirrors.rules[root].frame).reshape(4, 4)
                               @ np.array(original.frame).reshape(4, 4))
    assert session.command("mirror.source", target=identity) == child


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
