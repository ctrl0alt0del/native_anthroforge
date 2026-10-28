from dataclasses import replace

import numpy as np

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
