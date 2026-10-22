"""Evaluation snapshots retain validation without retaining stale records or edges."""

from dataclasses import replace
from unittest.mock import patch

import pytest

from anthroforge.application import geometry_outputs, tissue_results
from anthroforge.core import document_index, object_registry
from anthroforge.core.construction import Primitive
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.tissue_stacking import StackPlan
from tests.test_tissue_contracts import membrane_document


def update(document, item):
    return replace(
        document, objects=tuple(item if o.id == item.id else o for o in document.objects)
    )


def test_evaluated_publication_reuses_validation_and_links_without_stale_lookup():
    before, tissue = membrane_document()
    changed = replace(tissue, result=EvaluationResult(asset="new", revision=4))
    with patch.object(object_registry, "validate") as validation:
        with patch.object(document_index, "object_link") as links:
            after = update(before, changed)
    validation.assert_not_called()
    links.assert_not_called()
    assert after.index.structure is before.index.structure
    assert after.registry.consumers is before.registry.consumers
    assert after.object(tissue.id) is changed
    assert before.object(tissue.id) is tissue


def test_value_change_inspects_only_changed_links_but_revalidates_consumers():
    document, tissue = membrane_document()
    item = document.objects[0]
    changed = replace(item, points=(replace(item.points[0], radius=2), *item.points[1:]))
    with patch.object(document_index, "object_link", wraps=document_index.object_link) as links:
        after = update(document, changed)
    assert links.call_count == 1
    assert after.index.structure is document.index.structure
    with pytest.raises(ValueError, match="Workspace associations"):
        update(after, replace(changed, owners=(tissue.source,)))


def test_parent_context_changes_rebuild_transitive_frame_walks():
    document, tissue = membrane_document()
    curve = document.objects[0]
    changed = update(document, replace(curve, parent=document.entities[0].id))
    graph = changed.index.structure.dependencies
    assert Port(document.entities[0].id, "pose") in graph[Port(tissue.source, "geometry")]
    assert graph is not document.index.structure.dependencies


def test_derived_stacking_providers_are_relationship_changes():
    document, tissue = membrane_document()
    document = update(document, replace(tissue, stacking=True))
    changed = replace(document.object(tissue.id), stack_plan=StackPlan(providers=("missing",)))
    after = update(document, changed)
    assert Port("missing", "final") in after.index.structure.dependencies[Port(tissue.id, "final")]
    assert Port(tissue.id, "final") in after.index.structure.dependencies.blocked


def test_pending_tissues_publish_once_and_repeat_is_a_noop(session):
    document, tissue = membrane_document()
    other = replace(tissue, id="second")
    session.document = replace(document, objects=(*document.objects, other))
    ports = {Port(o.id, "rest") for o in (tissue, other)}
    with patch.object(session, "replace_document", wraps=session.replace_document) as publish:
        tissue_results.mark_pending(session, ports)
        tissue_results.mark_pending(session, ports)
    assert publish.call_count == 1
    assert all(session.document.object(p.owner).rest_result.status == "pending" for p in ports)


def test_geometry_pending_batches_anatomy_and_surface_and_ignores_empty_changes(session):
    document, tissue = membrane_document()
    bone = replace(document.entities[0], primitive=Primitive("IMPORTED", source="fixture"))
    session.document = replace(document, entities=(bone,))
    targets = {bone.id, tissue.source}
    with patch.object(session, "replace_document", wraps=session.replace_document) as publish:
        geometry_outputs.pending(session, set())
        geometry_outputs.pending(session, targets)
        geometry_outputs.pending(session, targets)
    assert publish.call_count == 1
    assert all(session.document.object(key).result.status == "pending" for key in targets)
    assert session.document.entity(bone.id).pose_revision == bone.pose_revision
