"""Owned worker snapshots assemble attached graphs; numerical capture/evaluation stays native."""

from dataclasses import fields, replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.membranes import Membrane
from anthroforge.core.object_outputs import output
from anthroforge.core.points import Point
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.surfaces import Surface

from . import (
    anchor_capture,
    dependencies,
    fiber_tasks,
    junction_copies,
    source_graph_copy,
    surface_evaluation,
    surface_results,
)
from .assets import Asset
from .construction_policy import revisions
from .curve_copy_resources import Copies
from .resources import Resources, references


def compute(session: Any, spec: Any, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    copier = Copies(resources, spec.identities)
    objects = construction(session, spec, document, copier, cancel)
    links = junction_copies.records(document, spec.identities)
    draft = replace(
        document, objects=(*document.objects, *objects), junctions=(*document.junctions, *links)
    )
    objects = evaluated_surfaces(session, draft, resources, objects, cancel)
    objects = with_tissue(objects, spec)
    draft = replace(draft, objects=(*document.objects, *objects))
    objects = tuple(provenance(draft, item) for item in objects)
    return document, objects, links, retained(resources, objects)


def construction(
    session: Any, spec: Any, document: Any, copier: Copies, cancel: Any
) -> tuple[Any, ...]:
    captures = {value.source: value for value in spec.fibers}
    rows = []
    for item in document.objects:
        if item.id not in spec.selected:
            continue
        if isinstance(item, Point):
            rows.append(point(session, spec.anchor, document, copier.resources, cancel))
        elif item.id in captures:
            rows.append(fiber(session, captures[item.id], document, copier.resources, cancel))
        else:
            rows.append(copied(item, spec, copier))
    return tuple(rows)


def point(session: Any, spec: Any, document: Any, resources: Any, cancel: Any) -> Any:
    _, item = anchor_capture.compute(session, spec, (document, resources), cancel)
    return replace(
        item, result=EvaluationResult(revision=1, authored_revision=item.construction_revision)
    )


def fiber(session: Any, spec: Any, document: Any, resources: Any, cancel: Any) -> Any:
    _, item, path, attachment = fiber_tasks.compute(session, spec, (document, resources), cancel)
    key = str(uuid4())
    result = EvaluationResult(key, 1, item.construction_revision)
    resources.paths[key] = path
    resources.attachments[item.attachment_asset] = attachment
    return replace(item, result=result)


def copied(item: Any, spec: Any, copier: Copies) -> Any:
    value = source_graph_copy.record(item, copier)
    if isinstance(value, Surface):
        value = Membrane(**{field.name: getattr(value, field.name) for field in fields(Surface)})
        value = replace(value, result=EvaluationResult())
    return replace(value, name=spec.name) if item.id == spec.source else value


def evaluated_surfaces(
    session: Any, document: Any, resources: Any, objects: Any, cancel: Any
) -> Any:
    return tuple(
        surface(session, document, resources, item, cancel) if isinstance(item, Surface) else item
        for item in objects
    )


def surface(session: Any, document: Any, resources: Any, item: Any, cancel: Any) -> Any:
    mesh = surface_evaluation.evaluate(session.engine, document, resources, item, cancel.handle)
    key = str(uuid4())
    resources.meshes[key] = Asset(mesh, "generated", "", 1.0, False)
    return surface_results.accepted(item, EvaluationResult(key, 1, item.construction_revision))


def with_tissue(objects: tuple[Any, ...], spec: Any) -> tuple[Any, ...]:
    from .tissue_operations import definition

    if not spec.tissue:
        return objects
    identity, name, preset = spec.tissue
    source = next(item for item in objects if item.id == spec.identities[spec.source])
    return (*objects, replace(definition(source, name, preset), id=identity))


def provenance(document: Any, item: Any) -> Any:
    if not isinstance(item, (Point, Curve, Surface)):
        return item
    inputs = dependencies.ports(document, Port(item.id, output(item)))
    pending = tuple(
        sorted({p.owner for p in inputs if document.object(p.owner).result.status == "pending"})
    )
    return replace(
        item, result=replace(item.result, inputs=revisions(document, inputs), pending=pending)
    )


def retained(resources: Resources, objects: Any) -> Resources:
    keys = references((), objects)
    return Resources(
        **{
            kind: {key: getattr(resources, kind)[key] for key in values}
            for kind, values in keys.items()
        }
    )
