"""Explicit curve-point identity sharing has distinct dependency outputs and file records."""

from dataclasses import replace

import pytest

from anthroforge.application import curve_copy, storage
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.document import Document
from anthroforge.core.junctions import Junction, PointRef, members, port
from anthroforge.core.results import Port


def linked():
    a = Curve((CurvePoint(), CurvePoint(position=(1, 0, 0))))
    b = Curve((CurvePoint(), CurvePoint(position=(0, 1, 0))))
    junction = Junction(PointRef(a.id, a.points[0].id))
    a = replace(a, points=(replace(a.points[0], junction=junction.id), a.points[1]))
    b = replace(b, points=(replace(b.points[0], junction=junction.id), b.points[1]))
    return Document(objects=(a, b), junctions=(junction,)), a, b, junction


def test_junction_is_explicit_and_has_no_anatomical_or_scene_wrapper():
    document, a, b, junction = linked()
    assert not document.entities and junction.id not in document.registry.records
    assert members(document.objects)[junction.id] == (
        PointRef(a.id, a.points[0].id),
        PointRef(b.id, b.points[0].id),
    )
    graph = document.index.structure.dependencies
    assert not graph[Port(a.id, "path")]
    assert port(junction) in graph[Port(b.id, "path")]
    assert graph[port(junction)] == {Port(a.id, "path"), Port(a.id, "pose")}
    assert not graph.blocked


def test_changing_only_junction_source_rebuilds_relationship_index():
    before, a, b, junction = linked()
    changed = replace(junction, source=PointRef(b.id, b.points[0].id))
    after = replace(before, junctions=(changed,))
    assert after.registry is not before.registry
    graph = after.index.structure.dependencies
    assert port(changed) in graph[Port(a.id, "path")]
    assert not graph[Port(b.id, "path")]
    assert not graph.blocked


def test_junction_cycles_are_authored_and_reported_as_actual_output_cycles():
    document, a, b, first = linked()
    second = Junction(PointRef(b.id, b.points[1].id))
    a = replace(a, points=(a.points[0], replace(a.points[1], junction=second.id)))
    b = replace(b, points=(b.points[0], replace(b.points[1], junction=second.id)))
    document = replace(document, objects=(a, b), junctions=(first, second))
    graph = document.index.structure.dependencies
    assert {Port(a.id, "path"), Port(b.id, "path"), port(first), port(second)} <= graph.blocked
    assert len(graph.cycles) == 1


def test_unknown_junction_and_missing_source_are_rejected():
    document, a, b, junction = linked()
    with pytest.raises(ValueError, match="resolve explicitly"):
        replace(document, junctions=())
    with pytest.raises(ValueError, match="source"):
        replace(document, junctions=(replace(junction, source=PointRef(a.id, b.points[0].id)),))
    with pytest.raises(ValueError, match="other member"):
        replace(document, objects=(a,))


def test_independent_curve_copy_drops_junction_relationship():
    _, a, _, _ = linked()
    copied = curve_copy.clone(a, curve_copy.mapping(a))
    assert not any(p.junction for p in copied.points)
    assert not Document(objects=(copied,)).junctions


def test_junction_identity_and_source_roundtrip_in_schema_three():
    document, _, _, junction = linked()
    encoded = storage.document_state(document)
    restored = storage.decode_document(encoded)
    assert restored == document and restored.junctions == (junction,)
    assert members(restored.objects) == members(document.objects)
