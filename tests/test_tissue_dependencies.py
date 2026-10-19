"""Phase-specific provenance and transitive topology constraints for attached tissue graphs."""

from dataclasses import replace

import pytest

from anthroforge.application import construction_policy, object_revisions
from anthroforge.core.points import Anchor
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.surface_references import SurfaceBinding, SurfaceReference
from tests.test_tissue_contracts import membrane_document


def test_classification_changes_do_not_invalidate_intrinsic_or_stack_outputs():
    _, tissue = membrane_document()
    changed = object_revisions.authored(tissue, replace(tissue, classification="FAT"))
    assert changed.classification == "FAT" and changed.generation == tissue.generation + 1
    assert not object_revisions.changed_ports(tissue, changed)
    assert changed.construction_revision == tissue.construction_revision


def test_stacking_settings_invalidate_plan_and_inflation_preserves_base():
    _, tissue = membrane_document()
    stacked = object_revisions.authored(tissue, replace(tissue, stacking=True))
    assert object_revisions.changed_ports(tissue, stacked) == {Port(tissue.id, "plan")}
    assert stacked.plan_revision == 1 and stacked.base_revision == stacked.rest_revision == 0
    side = replace(tissue.parts[0].a, inflation=replace(tissue.parts[0].a.inflation, amount=0.1))
    inflated = object_revisions.authored(
        tissue, replace(tissue, parts=(replace(tissue.parts[0], a=side),))
    )
    assert object_revisions.changed_ports(tissue, inflated) == {Port(tissue.id, "rest")}
    assert inflated.rest_revision == 1 and inflated.base_revision == 0


def test_final_revision_reads_final_result_instead_of_unstacked_display():
    document, tissue = membrane_document()
    item = replace(
        tissue, result=EvaluationResult(revision=19), final_result=EvaluationResult(revision=7)
    )
    document = replace(
        document, objects=tuple(item if o.id == tissue.id else o for o in document.objects)
    )
    assert construction_policy.revision(document, Port(tissue.id, "final")).accepted == 7


def test_tissue_target_locks_source_membrane_and_every_consumed_fiber_until_unbound():
    document, tissue = membrane_document()
    anchor = Anchor(binding=SurfaceBinding(SurfaceReference(tissue.id, "TISSUE_FINAL")))
    attached = replace(document, objects=(*document.objects, anchor))
    curve = document.object(tissue.source).curves[0].curve
    for key in (tissue.id, tissue.source, curve):
        with pytest.raises(ValueError, match="Topology is locked"):
            construction_policy.require_topology_edit(attached, key)
        construction_policy.require_topology_edit(document, key)
    locks = construction_policy.topology_locks(attached, curve)
    assert len(locks) == 1 and locks[0]["id"] == anchor.id
    assert locks[0]["consumer"] == tissue.id
    assert locks[0]["reason"] == "Incoming attachment on " + tissue.name
