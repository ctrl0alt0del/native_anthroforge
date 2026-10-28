"""Independent construction copies with one remapping for internally shared controls."""

from dataclasses import replace
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from anthroforge.core import graph_records
from anthroforge.core.construction import Control, Curve, Deformer, Primitive
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.results import EvaluationResult, ReadRevision

from . import curve_sources, junction_copies, shortcut_copies
from .curve_copy_resources import Copies

if TYPE_CHECKING:
    from .session import Session


def copied_controls(document: Document, entities: set[str]) -> set[str]:
    found = {
        b.control for e in document.entities if e.id in entities for b in e.deformers if b.control
    }
    pending = list(found)
    while pending:
        control = document.control(pending.pop())
        references = {b.control for b in control.deformers}
        references |= {control.follow} & {c.id for c in document.controls}
        pending.extend(references - found)
        found |= references
    return found


def identities(document: Document, entities: set[str], controls: set[str]) -> set[str]:
    result = entities | controls
    for item in document.entities:
        if item.id in entities:
            result |= {b.id for b in item.deformers}
            if item.primitive:
                result |= {c.id for c in item.primitive.curves}
                result |= {
                    p.id
                    for c in item.primitive.curves
                    for p in curve_sources.source(document, c.id).points
                }
                result |= {p.id for p in item.primitive.pieces}
    result |= {b.id for c in document.controls if c.id in controls for b in c.deformers}
    return result


def binding(source: Deformer, mapping: dict[str, str]) -> Deformer:
    return cast(Deformer, graph_records.rewritten(source, mapping))


def primitive(source: Primitive | None, mapping: dict[str, str]) -> Primitive | None:
    return cast(Primitive | None, graph_records.rewritten(source, mapping))


def control(source: Control, mapping: dict[str, str]) -> Control:
    return replace(
        source,
        id=mapping[source.id],
        name=source.name + " copy",
        generation=0,
        follow=mapping.get(source.follow, source.follow),
        owners=tuple(mapping.get(k, k) for k in source.owners),
        deformers=tuple(binding(b, mapping) for b in source.deformers),
        result=replace(source.result, inputs=remap_inputs(source.result.inputs, mapping)),
    )


def entity(source: SCP, mapping: dict[str, str], parent: str) -> SCP:
    assert source.primitive is None or isinstance(source.primitive, Primitive)
    return replace(
        source,
        id=mapping[source.id],
        name=source.name + " copy",
        generation=0,
        parent=mapping.get(source.parent, parent),
        primitive=primitive(source.primitive, mapping),
        deformers=tuple(binding(b, mapping) for b in source.deformers),
        result=remap_result(source.result, mapping),
    )


def remap_inputs(
    inputs: tuple[ReadRevision, ...], mapping: dict[str, str]
) -> tuple[ReadRevision, ...]:
    return tuple(
        replace(
            value,
            owner=mapping.get(value.owner, value.owner),
            output=remap_output(value.output, mapping, value.owner),
            membership=tuple(sorted(mapping.get(key, key) for key in value.membership)),
        )
        for value in inputs
    )


def remap_output(output: str, mapping: dict[str, str], owner: str = "") -> str:
    from anthroforge.core.formula_dependencies import property_port, property_reference
    from anthroforge.core.results import Port

    if output.startswith("property:"):
        reference = property_reference(Port(owner, output))
        return property_port(shortcut_copies.reference(reference, mapping)).output
    if output.startswith("junction:"):
        return "junction:" + mapping.get(output[9:], output[9:])
    return output


def remap_result(result: EvaluationResult, mapping: dict[str, str]) -> EvaluationResult:
    return replace(
        result,
        inputs=remap_inputs(result.inputs, mapping),
        pending=tuple(mapping.get(key, key) for key in result.pending),
    )


def duplicate(session: "Session", ids: set[str], parent: str) -> dict[str, str]:
    controls = copied_controls(session.document, ids)
    mapping = {key: str(uuid4()) for key in identities(session.document, ids, controls)}
    mapping = junction_copies.identities(session.document, mapping)
    copies = tuple(entity(e, mapping, parent) for e in session.document.entities if e.id in ids)
    shared = tuple(control(c, mapping) for c in session.document.controls if c.id in controls)
    junctions = session.document.junctions + junction_copies.records(session.document, mapping)
    session.replace_document(
        entities=(*session.document.entities, *copies),
        controls=(*session.document.controls, *shared),
        objects=(*session.document.objects, *copied_curves(session, mapping)),
        junctions=junctions,
        **shortcut_copies.state(session.document, mapping),
    )
    return {key: mapping[key] for key in ids}


def copied_curves(session: "Session", mapping: dict[str, str]) -> tuple[Curve, ...]:
    copies = Copies(session.resources, mapping)
    return tuple(
        copies.record(item)
        for item in session.document.objects
        if isinstance(item, Curve) and item.id in mapping
    )
