from dataclasses import replace
from threading import Event

import numpy as np

from anthroforge.application import assembly_preparation, assembly_source, storage
from anthroforge.application.object_frames import Frames
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from tests.test_assembly_graph import graph_document
from tests.test_fiber_creation import bind, scene


def captured(session, tmp_path):
    target, curve = scene(session)
    fiber = bind(session, target, curve)
    path = tmp_path / "fiber.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    return target, fiber, assembly_source.inspect(str(path), Event())


def prepared(session, source, keys, options=None, destination=None):
    destination = destination or session.document
    return assembly_preparation.prepare(
        source, keys, options or {}, session.engine, (destination, session.resources), Event()
    )


def test_missing_fiber_support_is_a_reference_not_anatomy(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    destination = Document()
    value = prepared(session, source, [fiber.id], destination=destination)
    merged = value.merge(destination)
    copied = merged.object(value.identities[fiber.id])
    assert not merged.entities and merged.external_references
    assert copied.bindings[0].target not in merged.registry.records
    assert all(r.source_entity == target for r in merged.external_references)
    assert copied.attachment_asset in value.resources.attachments
    assert copied.result.status == "invalid" and copied.result.asset


def test_excluded_transform_parent_requires_explicit_choice(session, tmp_path):
    document = graph_document()
    curve, other = document.objects
    document = replace(document, objects=(replace(curve, parent="root"), other))
    path = tmp_path / "curves.anthroforge"
    storage.atomic_save(path, document, session.resources)
    source = assembly_source.inspect(str(path), Event())
    value = prepared(session, source, [curve.id])
    assert not value.ready and "detach" in value.findings[0]["message"]
    options = dict(mappings={"root": dict(action="detach")})
    value = prepared(session, source, [curve.id], options)
    assert value.ready
    assert not value.references
    assert value.merge(session.document).object(value.identities[curve.id]).parent == ""


def test_mapped_transform_parent_keeps_world_placement(session, tmp_path):
    document = graph_document()
    curve, other = document.objects
    matrix = (1.0, 0.0, 0.0, 2.0, 0.0, 1.0, 0.0, 3.0, 0.0, 0.0, 1.0, 4.0, 0.0, 0.0, 0.0, 1.0)
    document = replace(document, objects=(replace(curve, parent="root", matrix=matrix), other))
    path = tmp_path / "placed.anthroforge"
    storage.atomic_save(path, document, session.resources)
    source = assembly_source.inspect(str(path), Event())
    destination = Document(entities=(SCP("Other", id="other", matrix=matrix),))
    value = prepared(session, source, [curve.id], dict(mappings={"root": "other"}), destination)
    result = value.merge(destination)
    np.testing.assert_allclose(
        Frames(session.engine, result).world(value.identities[curve.id]), matrix
    )
