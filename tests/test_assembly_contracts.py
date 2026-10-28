from dataclasses import replace

import pytest

from anthroforge.application.storage import decode_document, document_state
from anthroforge.core.assembly import ExternalReference, ImportProvenance, ReferenceUse
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.document import Document
from anthroforge.core.graph_records import owned, references, rewritten
from anthroforge.core.numeric_properties import PropertyRef
from anthroforge.core.points import Anchor
from anthroforge.core.surface_references import SurfaceBinding, SurfaceReference


def declared_document():
    anchor = Anchor(id="anchor", binding=SurfaceBinding(SurfaceReference("external")))
    use = ReferenceUse(anchor.id, "support", "point", "SCP_GEOMETRY")
    ref = ExternalReference("external", "project", "bone", 3, "Bone", "SCP", (use,))
    return Document(objects=(anchor,), external_references=(ref,))


def test_declared_external_is_not_a_placeholder_scene_object():
    document = declared_document()
    assert set(document.registry.records) == {"anchor"}
    with pytest.raises(ValueError, match="Resolve imported reference"):
        document.object("external")
    with pytest.raises(ValueError):
        replace(document, external_references=())


def test_external_kind_does_not_fabricate_surface_capability():
    document = declared_document()
    invalid = replace(document.external_references[0], kind="CURVE")
    with pytest.raises(ValueError, match="surface"):
        replace(document, external_references=(invalid,))


def test_provenance_and_unresolved_relationships_round_trip():
    document = declared_document()
    provenance = ImportProvenance("batch", "project", 3, "digest", "Source", (("old", "anchor"),))
    document = replace(document, imports=(provenance,))
    restored = decode_document(document_state(document))
    assert restored.external_references == document.external_references
    assert restored.imports == document.imports
    assert restored.objects == document.objects


def test_typed_remap_preserves_text_and_rewrites_owned_points_and_references():
    curve = Curve((CurvePoint(id="p"), CurvePoint(id="q")), id="curve", name="p", parent="bone")
    mapping = {key: "copy-" + key for key in owned(curve)} | {"bone": "target"}
    copied = rewritten(curve, mapping)
    assert owned(copied) == {"copy-curve", "copy-p", "copy-q"}
    assert copied.name == "p" and copied.parent == "target"
    assert [(r.relationship, r.target) for r in references(copied)] == [("parent", "target")]


def test_property_components_remap_without_rewriting_formula_text():
    reference = PropertyRef("curve", ("points", "@p", "position"), 2)
    assert rewritten(reference, {"curve": "c", "p": "p2"}) == PropertyRef(
        "c", ("points", "@p2", "position"), 2
    )
