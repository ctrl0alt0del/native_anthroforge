"""Tissue model substitution, ownership, stage identity and strict storage contracts."""

import json
from dataclasses import replace

import pytest

from anthroforge.application import object_codec, storage
from anthroforge.application.resources import referenced
from anthroforge.application.transform_policy import require_object_transform
from anthroforge.core import anatomical_surfaces
from anthroforge.core.construction import CurvePoint
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber, FiberBinding
from anthroforge.core.membranes import Membrane
from anthroforge.core.points import Anchor, Point
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surface_references import SurfaceBinding, SurfaceReference
from anthroforge.core.surfaces import Surface
from anthroforge.core.tissue_settings import TissueInflation, TissuePart, TissueSide
from anthroforge.core.tissues import TissueVCP


def membrane_document():
    bone = SCP("Bone")
    rows = tuple(fiber(bone, y) for y in (0, 1))
    surface = Membrane(curves=tuple(CurveUse(row.id) for row in rows))
    tissue = TissueVCP(source=surface.id)
    return Document(entities=(bone,), objects=(*rows, surface, tissue)), tissue


def fiber(bone, y):
    points = tuple(CurvePoint(position=(x, y, 0)) for x in (0, 1))
    return Fiber(points, bindings=tuple(FiberBinding(p.id, bone.id) for p in points))


def test_anchor_and_membrane_preserve_generic_source_contracts():
    bone = SCP("Bone")
    anchor = Anchor(binding=SurfaceBinding(SurfaceReference(bone.id)))
    document, tissue = membrane_document()
    assert isinstance(anchor, Point)
    assert isinstance(document.object(tissue.source), Surface)
    assert tissue.id in document.registry.anatomy
    assert tissue.id not in document.registry.construction
    assert document.registry.consumers[tissue.source] == {tissue.id}


def test_point_only_document_needs_no_dummy_scp():
    point = Point(position=(1, 2, 3))
    document = Document(objects=(point,))
    assert document.object(point.id) is point
    assert not document.registry.anatomy


def test_membrane_cannot_silently_consume_an_unbound_curve():
    from anthroforge.core.construction import Curve

    document, tissue = membrane_document()
    first = document.objects[0]
    unbound = Curve(first.points, id=first.id)
    with pytest.raises(ValueError, match="Membrane sources"):
        replace(document, objects=(unbound, *document.objects[1:]))


def test_tissue_rejects_generic_surface_until_attached_conversion():
    document, tissue = membrane_document()
    original = document.object(tissue.source)
    generic = Surface(id=original.id, curves=original.curves)
    with pytest.raises(ValueError, match="Anchor, Fiber or Membrane"):
        replace(document, objects=(*document.objects[:2], generic, tissue))


def test_classification_does_not_change_strategies_or_stacking():
    document, tissue = membrane_document()
    fat = replace(tissue, classification="FAT")
    changed = replace(document, objects=(*document.objects[:-1], fat))
    assert changed.object(fat.id).parts == tissue.parts
    assert fat.stacking == tissue.stacking
    with pytest.raises(ValueError, match="derived"):
        require_object_transform(fat)


def test_surface_only_stacking_is_a_construction_capability():
    document, tissue = membrane_document()
    source = document.objects[0]
    sweep = TissuePart(a=TissueSide(TissueInflation(mode="PROFILE")))
    candidate = replace(tissue, source=source.id, parts=(sweep,), stacking=True)
    with pytest.raises(ValueError, match="surface-based"):
        replace(document, objects=(*document.objects[:-1], candidate))


def test_final_provider_never_uses_the_display_fallback():
    document, tissue = membrane_document()
    previous = EvaluationResult(asset="accepted-final", status="failed")
    failed = replace(tissue, result=EvaluationResult(asset="own-only"), final_result=previous)
    assert anatomical_surfaces.result(failed, "TISSUE_FINAL") is previous
    assert anatomical_surfaces.result(failed, "TISSUE_FINAL").asset != failed.result.asset
    with pytest.raises(ValueError, match="requested"):
        anatomical_surfaces.reference(tissue.id, document.registry.records, "SCP_GEOMETRY")


def test_tissue_results_are_all_owned_by_document_resources():
    from anthroforge.core.tissue_base import TissueBaseState

    document, tissue = membrane_document()
    states = {
        name: EvaluationResult(asset=name)
        for name in ("base_result", "rest_result", "intrinsic_result", "final_result")
    }
    tissue = replace(tissue, base_state=TissueBaseState("SURFACE"), **states)
    changed = replace(document, objects=(*document.objects[:-1], tissue))
    assert referenced(changed)["meshes"] == set(states)


def test_typed_tissue_records_round_trip_without_runtime_handles():
    document, tissue = membrane_document()
    for item in document.objects:
        encoded = json.loads(json.dumps(object_codec.encode(item)))
        assert object_codec.decode(encoded) == item
    assert storage.VERSION == 6 and {4, 5}.issubset(storage.READ_VERSIONS)
