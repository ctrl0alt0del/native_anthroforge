from dataclasses import replace
from threading import Event

import numpy as np

from anthroforge.application import assembly_source, storage
from anthroforge.application.assets import imported
from anthroforge.core.document import Document
from anthroforge.native.mesh import NativeCancellation
from tests.test_assembly_mapping import captured, prepared
from tests.test_fiber_creation import CUBE


def test_identical_geometry_retains_material_bindings_and_dense_fields(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    value = prepared(session, source, [fiber.id], dict(mappings={target: target}))
    copied = value.merge(session.document).object(value.identities[fiber.id])
    assert value.ready and copied.result.status == "ready"
    assert copied.bindings[0].attachment.binding == fiber.bindings[0].attachment.binding
    before = session.resources.attachments[fiber.attachment_asset].field
    after = value.resources.attachments[copied.attachment_asset].field
    np.testing.assert_array_equal(before.bindings, after.bindings)
    assert not value.evidence


def changed_target(session, target):
    before = session.document.entity(target)
    cancel = NativeCancellation(session.engine)
    session.assets["different"] = imported(session.engine, CUBE, 0.5, False, cancel)
    updated = replace(before, asset="different", result=replace(before.result, asset="different"))
    return Document(entities=(updated,))


def test_same_counts_do_not_establish_correspondence(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    destination = changed_target(session, target)
    value = prepared(session, source, [fiber.id], dict(mappings={target: target}), destination)
    assert not value.ready
    assert "Rebind" in value.findings[0]["message"]


def test_explicit_rebind_prepares_current_shape_and_new_capture(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    destination = changed_target(session, target)
    options = dict(mappings={target: dict(action="map", target=target, rebind=True)})
    value = prepared(session, source, [fiber.id], options, destination)
    assert value.ready and value.evidence
    copied = value.merge(destination).object(value.identities[fiber.id])
    assert copied.bindings[0].attachment.binding != fiber.bindings[0].attachment.binding


def test_legacy_capture_frames_match_normal_project_loading(session, tmp_path):
    target, fiber, _ = captured(session, tmp_path)
    key = fiber.attachment_asset
    strip_frame_metadata(session, key)
    path = tmp_path / "legacy-capture.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    _, normal = storage.read_package(path, session.engine)
    source = assembly_source.inspect(str(path), Event())
    candidate = prepared(session, source, [fiber.id], dict(mappings={target: target}))
    copied = candidate.merge(session.document).object(candidate.identities[fiber.id])
    transferred = candidate.resources.attachments[copied.attachment_asset].field
    assert transferred.frame_hints == normal.attachments[key].field.frame_hints
    assert transferred.world == normal.attachments[key].field.world


def strip_frame_metadata(session, key):
    asset = session.resources.attachments[key]
    session.resources.attachments[key] = replace(
        asset, field=replace(asset.field, frames=(), frame_hints=())
    )
