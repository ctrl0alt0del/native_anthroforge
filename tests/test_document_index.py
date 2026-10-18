from dataclasses import replace

import pytest

from anthroforge.application import dependencies
from anthroforge.application.curve_sources import create_records
from anthroforge.application.primitive_operations import default_primitive
from anthroforge.application.resources import Resources
from anthroforge.application.storage import decode_document, manifest
from anthroforge.core.construction import Control, Deformer, Target
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Attachment
from anthroforge.core.results import Port


def body_document():
    primitive, curves = create_records(default_primitive("BODY", "CAPSULE"), "body")
    return Document(entities=(SCP("Body", id="body", primitive=primitive),), objects=curves)


def test_value_edits_share_structure_but_keep_snapshot_values_independent():
    before = body_document()
    item = before.entity("body")
    curve = before.object(item.primitive.curves[0].id)
    point = replace(curve.points[0], position=(0, 1, 0))
    changed = replace(curve, points=(point, *curve.points[1:]))
    after = replace(before, objects=(changed,))
    assert after.object(curve.id) == changed
    assert before.entity("body") is item
    assert after.index.structure is before.index.structure
    assert replace(after, revision=7).index is after.index
    with pytest.raises(TypeError):
        after.index.entities["body"] = item


def test_cached_validation_rejects_changed_global_identities_and_parent_links():
    document = body_document()
    item = document.entity("body")
    curve = document.object(item.primitive.curves[0].id)
    point = replace(curve.points[0], id=item.id)
    curve = replace(curve, points=(point, *curve.points[1:]))
    with pytest.raises(ValueError, match="unique"):
        replace(document, objects=(curve,))
    with pytest.raises(ValueError, match="tree"):
        replace(document, entities=(replace(item, parent="missing"),))


def hooked_document():
    document = body_document()
    control = Control("Hook", "HOOK", id="hook", follow="body")
    binding = Deformer("HOOK", "hook", Target("body"))
    item = replace(document.entity("body"), deformers=(binding,))
    return replace(document, entities=(item,), controls=(control,))


def test_graph_reuse_tracks_enabling_and_distinguishes_pose_from_geometry_cycles():
    document = hooked_document()
    graph = dependencies.graph(document)
    assert not dependencies.blocked(graph)
    control = replace(document.control("hook"), follow="hook")
    cyclic = replace(document, controls=(control,))
    assert Port("body", "geometry") in dependencies.blocked(dependencies.graph(cyclic))
    item = document.entity("body")
    disabled = replace(item, deformers=(replace(item.deformers[0], enabled=False),))
    changed = replace(cyclic, entities=(disabled,))
    assert Port("body", "geometry") not in dependencies.blocked(dependencies.graph(changed))
    assert Port("hook", "control") in dependencies.blocked(dependencies.graph(changed))
    assert dependencies.graph(document) is graph and not dependencies.blocked(graph)


def test_cached_validation_rejects_control_removal_with_live_bindings():
    document = hooked_document()
    with pytest.raises(ValueError, match="matching kind"):
        replace(document, controls=())
    with pytest.raises(ValueError, match="source does not exist"):
        replace(document, controls=(replace(document.control("hook"), follow="missing"),))


def test_attachment_modes_and_global_freeze_update_dependency_edges():
    root = SCP("Root", id="root")
    child = SCP("Child", id="child", parent="root")
    document = Document(entities=(root, child))
    assert Port("root", "geometry") in dependencies.graph(document)[Port("child", "pose")]
    child = replace(child, attachment=Attachment(parent_mode="OBJECT_ORIGIN"))
    changed = replace(document, entities=(root, child))
    assert dependencies.graph(changed)[Port("child", "pose")] == {Port("root", "pose")}
    frozen = replace(document, attachments_enabled=False)
    assert not dependencies.graph(frozen)[Port("child", "pose")]


def test_indexes_are_derived_and_do_not_enter_project_schema():
    document = hooked_document()
    data = manifest(document, Resources())["document"]
    assert "_index" not in data
    restored = decode_document(data)
    assert restored == document
    assert restored.index is not document.index
    assert dependencies.graph(restored) == dependencies.graph(document)
