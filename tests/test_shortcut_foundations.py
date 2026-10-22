"""Stable wrappers, coherent candidates and backward-reading document contracts."""

from dataclasses import asdict, replace

import pytest

from anthroforge.application import shortcut_ownership, storage
from anthroforge.core import numeric_properties as numeric
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.shortcuts import DrivingFormula, DrivingShortcut, FormulaInput, Shortcut
from anthroforge.core.tissue_settings import TissueInflation


def test_references_survive_point_reordering_and_renaming():
    a, b = CurvePoint(), CurvePoint(position=(1, 0, 0))
    curve = Curve((a, b))
    ref = numeric.PropertyRef(curve.id, ("points", "@" + a.id, "position"), 0)
    shortcut = Shortcut(ref, exposed=True)
    changed = replace(curve, name="Renamed", points=(b, a))
    result = numeric.changed(changed, ref, 0.25)
    assert result.points[1].position == (0.25, 0, 0)
    assert Shortcut(ref).id == shortcut.id


def test_coherent_candidate_validates_coupled_values_once():
    original = TissueInflation(minimum=0.0, amount=0.02)
    low = numeric.PropertyRef("tissue", ("minimum",))
    high = numeric.PropertyRef("tissue", ("amount",))
    result = numeric.batch(original, ((low, 0.03), (high, 0.04)))
    assert (result.minimum, result.amount) == (0.03, 0.04)
    with pytest.raises(ValueError, match="Minimum thickness"):
        numeric.batch(original, ((low, 0.015), (high, 0.01)))
    assert original.amount == 0.02


def test_numeric_types_do_not_coerce_real_to_integer():
    ref = numeric.PropertyRef("curve", ("resolution",))
    descriptor = numeric.NumericDescriptor(ref, "Resolution", "INTEGER")
    assert descriptor.validate(12) == 12
    for value in (12.0, True, float("inf")):
        with pytest.raises(ValueError):
            descriptor.validate(value)


def test_driver_ownership_includes_only_actual_downstream_components():
    root = SCP("Root")
    child = SCP("Child", parent=root.id)
    x = numeric.PropertyRef(root.id, ("geometry_offset",), 0)
    y = replace(x, component=1)
    first = DrivingShortcut(formulas=(DrivingFormula(x, "value"),))
    second = DrivingShortcut(formulas=(DrivingFormula(y, "value"),))
    inp = FormulaInput("x", property=x)
    third = DrivingShortcut(formulas=(DrivingFormula(replace(x, target=child.id), "x", (inp,)),))
    document = Document(entities=(root, child), driving_shortcuts=(first, second, third))
    assert shortcut_ownership.owners(document, first) == {root.id, child.id}
    assert shortcut_ownership.scp_owner(document, first) == ""
    assert shortcut_ownership.scp_owner(document, second) == root.id


def test_exposure_does_not_edit_property_and_property_has_no_policy(session):
    curve = session.command("curve.create")
    ref = dict(target=curve, path=["engine_settings", "resolution"])
    session.command("wait")
    before = session.document.object(curve)
    key = session.command("shortcut.expose", reference=ref, label="Detail")
    assert session.document.object(curve) is before
    session.command("property.set", reference=ref, value=12)
    assert session.document.object(curve).engine_settings.resolution == 12
    assert session.command("shortcut.inspect", reference=ref)["id"] == key
    session.command("undo")
    assert session.document.object(curve).engine_settings.resolution == 24


def test_shortcuts_roundtrip_and_old_document_initializes_empty():
    root = SCP("Root")
    ref = numeric.PropertyRef(root.id, ("geometry_offset",), 0)
    document = Document(entities=(root,), shortcuts=(Shortcut(ref, "Offset", True),))
    state = storage.document_state(document)
    assert storage.decode_document(state) == document
    for field in ("shortcuts", "driving_shortcuts", "formula_results"):
        state.pop(field)
    assert storage.decode_document(state).shortcuts == ()
    assert asdict(document.shortcuts[0])["reference"]["component"] == 0
