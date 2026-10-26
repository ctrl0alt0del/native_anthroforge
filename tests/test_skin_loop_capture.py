"""Application guide capture follows accepted Fiber paths without presentation dependence."""

from dataclasses import replace

from anthroforge.application import skin_loop_capture
from anthroforge.core.skin import TopologySettings
from anthroforge.native.mesh import NativeCancellation
from tests.test_fiber_creation import bind, scene


def test_closed_fiber_is_captured_for_both_backends_without_mutation(session):
    bone, source = scene(session, closed=True)
    fiber = bind(session, bone, source)
    before = session.document
    mesh = session.assets[before.object(bone).result.asset].mesh
    token = NativeCancellation(session.engine)
    for backend in ("INSTANT", "QUADWILD"):
        document = replace(
            before, skin=replace(before.skin, topology_settings=TopologySettings(backend=backend))
        )
        result = skin_loop_capture.capture(session.engine, document, session.resources, mesh, token)
        assert [row.identity.owner for row in result.sources] == [fiber.id]
        assert result.data.statuses.tolist() == [1]
        assert "unpaired" in result.warnings[0]
    assert session.document is before


def test_manual_pending_authored_closure_does_not_replace_accepted_guide(session):
    bone, source = scene(session, closed=True)
    fiber = bind(session, bone, source)
    document = session.document
    extra = replace(fiber.bindings[0], point=fiber.points[-1].id)
    changed = replace(fiber, closed=False, bindings=(*fiber.bindings, extra))
    objects = tuple(changed if item.id == fiber.id else item for item in document.objects)
    document = replace(document, objects=objects)
    token = NativeCancellation(session.engine)
    rows, warnings = skin_loop_capture.sources(session.engine, document, session.resources, token)
    assert not warnings and [row.identity.owner for row in rows] == [fiber.id]
    assert rows[0].mesh.closed
