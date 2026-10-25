"""Authored supports are independent from accepted fields, pins and routing obstacles."""

from dataclasses import asdict

import numpy as np
import pytest

from anthroforge.application import storage
from anthroforge.application.fiber_supports import selected_targets
from anthroforge.core.fiber_support_policy import FiberSupportPolicy
from anthroforge.core.surface_references import SurfaceReference
from tests.test_fiber_creation import bind, path, scene


@pytest.fixture(autouse=True, params=["SMOOTH_SHAPE", "LOCAL_SURFACE"])
def propagation(session, request):
    session.command("preferences.set", fiber_propagation=request.param)


def test_support_policy_preserves_pins_and_filters_automatic_candidates():
    parent, other, tissue = (
        SurfaceReference("p"),
        SurfaceReference("o"),
        SurfaceReference("t", "TISSUE_FINAL"),
    )
    policy = FiberSupportPolicy(included=(tissue,), excluded=(other,))
    assert set(selected_targets((parent, other), (parent,), policy)) == {parent, tissue}
    assert selected_targets((parent, other), (parent,), FiberSupportPolicy(False)) == (parent,)
    with pytest.raises(ValueError, match="included and excluded"):
        FiberSupportPolicy(included=(parent,), excluded=(parent,))


def test_configuring_supports_preserves_current_shape_and_roundtrips(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before = path(session, fiber.id)
    session.command("fiber.supports.configure", curve=fiber.id, policy=dict(automatic=False))
    session.wait()
    assert not session.scheduler.errors
    current = session.document.object(fiber.id)
    assert not current.support_policy.automatic
    np.testing.assert_allclose(path(session, fiber.id), before, atol=1e-10)
    assert storage.decode_document(storage.document_state(session.document)) == session.document
    session.command("undo")
    assert session.document.object(fiber.id).support_policy.automatic


def test_required_pin_cannot_be_excluded_and_inspection_is_read_only(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    ref = asdict(fiber.bindings[0].reference)
    with pytest.raises(ValueError, match="required"):
        session.command("fiber.supports.configure", curve=fiber.id, policy=dict(excluded=[ref]))
    before = session.document
    result = session.command("fiber.supports.inspect", curve=fiber.id)
    assert result["policy"]["automatic"]
    assert session.document is before


def test_explicit_tissue_support_is_not_a_routing_obstacle(session):
    from tests.test_fiber_support_policy import source_curve
    from tests.test_tissue_fiber_material import fiber_on_tissue

    tissue, template = fiber_on_tissue(session)
    fiber = bind(session, session.document.entities[0].id, source_curve(session, template))
    ref = dict(target=tissue, role="TISSUE_FINAL")
    session.command("fiber.supports.configure", curve=fiber.id, policy=dict(included=[ref]))
    session.wait()
    assert not session.scheduler.errors
    current = session.document.object(fiber.id)
    assert current.support_policy.included == (SurfaceReference(**ref),)
    assert any(s.reference.target == tissue for s in current.supports)
    assert current.engine_settings == fiber.engine_settings
