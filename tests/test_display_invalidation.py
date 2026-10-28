"""Projection work follows presentation dependencies without changing evaluation."""

from dataclasses import replace

from anthroforge.application.changes import DocumentChanges
from anthroforge.application.primitive_operations import straight_curve
from anthroforge.core.construction import Control
from anthroforge.core.document import Document
from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.desktop.construction_changes import ConstructionChanges
from anthroforge.desktop.display_transforms import DisplayTransforms


def document():
    root = SCP("Root", id="root")
    child = SCP("Child", id="child", parent=root.id)
    control = Control("Hook", "HOOK", id="hook", follow=root.id)
    curve = replace(straight_curve(), id="curve", parent=control.id)
    other = replace(straight_curve(), id="other", parent=child.id)
    return Document(entities=(root, child), controls=(control,), objects=(curve, other))


def test_projection_follows_ordinary_parents_but_not_anatomical_parent_poses():
    doc, tracker = document(), ConstructionChanges()
    assert tracker.targets(doc, DocumentChanges(), True) == {"curve", "other"}
    changes = DocumentChanges(entities={"root": {"matrix"}})
    assert tracker.targets(doc, changes, False) == {"root", "hook", "curve"}
    changes = DocumentChanges(objects={"curve": {"result"}})
    assert tracker.targets(doc, changes, False) == {"curve"}
    changes = DocumentChanges(entities={"root": {"result"}})
    assert tracker.targets(doc, changes, False) == set()


def test_projection_rebuilds_relationships_after_reparent_and_undo():
    doc, tracker = document(), ConstructionChanges()
    tracker.targets(doc, DocumentChanges(), True)
    changed = replace(doc, objects=(replace(doc.objects[0], parent="child"), doc.objects[1]))
    assert tracker.targets(changed, DocumentChanges(objects={"curve": {"parent"}}), False)
    pose = DocumentChanges(entities={"root": {"matrix"}})
    assert tracker.targets(changed, pose, False) == {"root", "hook"}
    tracker.targets(doc, DocumentChanges(objects={"curve": {"parent"}}), False)
    assert tracker.targets(doc, pose, False) == {"root", "hook", "curve"}


def test_display_transform_reuse_distinguishes_inspection_offsets_and_releases_old(monkeypatch):
    calls, cache = [], DisplayTransforms()
    monkeypatch.setattr(
        "anthroforge.desktop.display_transforms.geometry_matrix",
        lambda engine, matrix, offset: calls.append(offset) or matrix,
    )
    rows = [dict(matrix=IDENTITY, geometry_offset=(0, 0, 0))] * 4
    for row in rows:
        cache.matrix(None, row)
    offset = dict(rows[0], geometry_offset=(1, 0, 0))
    cache.retain((*rows, offset))
    cache.matrix(None, offset)
    assert len(calls) == 2 and len(cache.values) == 2
    cache.retain([offset])
    assert len(cache.values) == 1
