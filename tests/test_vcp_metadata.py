"""Optimization preserves provenance order and cross-record strategy validation."""

from dataclasses import replace
from unittest.mock import patch

import pytest

from anthroforge.application.evaluation_results import accepted_result
from anthroforge.core import object_registry
from anthroforge.core.results import EvaluationResult, Port
from tests.test_snapshot_publication import update
from tests.test_tissue_contracts import membrane_document


def test_pending_provenance_deduplicates_ports_in_document_order():
    document, tissue = membrane_document()
    for value in document.objects:
        document = update(document, replace(value, result=EvaluationResult(status="pending")))
    inputs = {Port(o.id, stage) for o in document.objects for stage in ("pose", "geometry")}
    result = accepted_result(document, tissue, inputs, "accepted")
    assert result.pending == tuple(o.id for o in document.objects if o.id != tissue.id)


def test_tissue_values_reuse_relationships_and_keep_current_records():
    document, tissue = membrane_document()
    changed = replace(tissue, resolution=32, reverse=True)
    with patch.object(object_registry, "validate") as validation:
        after = update(document, changed)
    validation.assert_not_called()
    assert after.registry.consumers is document.registry.consumers
    assert after.object(tissue.id) is changed
    assert document.object(tissue.id) is tissue


def test_local_strategy_edit_still_rejects_incompatible_inflation():
    document, tissue = membrane_document()
    side = replace(tissue.parts[0].a, inflation=replace(tissue.parts[0].a.inflation, mode="RADIAL"))
    changed = replace(tissue, parts=(replace(tissue.parts[0], a=side),))
    with pytest.raises(ValueError, match="unsupported"):
        update(document, changed)


def test_external_source_change_rechecks_existing_tissue_capabilities():
    document, tissue = membrane_document()
    source = document.object(tissue.source)
    side = replace(
        tissue.parts[0].a, inflation=replace(tissue.parts[0].a.inflation, mode="SECTION_PROFILE")
    )
    document = update(document, replace(tissue, parts=(replace(tissue.parts[0], a=side),)))
    with pytest.raises(ValueError, match="unsupported"):
        update(document, replace(source, close_across=True))
