from dataclasses import replace

from anthroforge.application import assembly_graph, assembly_selection
from anthroforge.core.construction import Curve, CurvePoint, Primitive
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.junctions import Junction, PointRef


def graph_document():
    a = Curve((CurvePoint(id="p"), CurvePoint(id="q")), id="a")
    b = Curve((CurvePoint(id="r"), CurvePoint(id="s")), id="b")
    root = SCP("Root", id="root")
    loft = Primitive("LOFT", curves=(CurveUse("a"), CurveUse("b")))
    child = SCP("Loft", id="child", parent="root", primitive=loft)
    return Document(entities=(root, child), objects=(a, b))


def test_selection_copies_required_sources_without_the_external_skeleton():
    document = graph_document()
    selected = assembly_selection.expand(document, ["child"])
    assert set(selected.records) == {"child", "a", "b"}
    assert assembly_graph.roots(selected) == ("child",)
    assert assembly_graph.boundaries(document, selected) == ()


def test_shared_junction_participants_are_copied_once_without_their_consumers():
    document = graph_document()
    a, b = document.objects
    a = replace(a, points=(replace(a.points[0], junction="j"), a.points[1]))
    b = replace(b, points=(replace(b.points[0], junction="j"), b.points[1]))
    junction = Junction(PointRef("a", "p"), "j")
    document = replace(document, objects=(a, b), junctions=(junction,))
    selected = assembly_selection.expand(document, ["a"])
    assert set(selected.records) == {"a", "b"}
    assert selected.junctions == (junction,)
    assert len(assembly_graph.identities(selected)) == 7


def test_transform_and_association_boundaries_have_separate_decisions():
    document = graph_document()
    a, b = document.objects
    document = replace(document, objects=(replace(a, parent="root", owners=("root",)), b))
    selected = assembly_selection.expand(document, ["a"])
    rows = assembly_graph.boundaries(document, selected)
    assert {r.relationship for r in rows} == {"parent", "association"}
    assert {r.source for r in rows} == {"root"}
    assert len({r.key for r in rows}) == 2
