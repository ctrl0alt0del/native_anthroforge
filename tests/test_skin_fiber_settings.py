"""Topology guides never become physical skin contributors or deformation supports."""

from dataclasses import asdict

import numpy as np
import pytest

from anthroforge.application import (
    skin_capture,
    skin_codec,
    skin_inputs,
    skin_operations,
    skin_topology_capture,
)
from anthroforge.application.construction_policy import revisions
from anthroforge.core.skin import Skin
from anthroforge.native.mesh import NativeCancellation
from tests.test_fiber_creation import bind, scene


def capture(session, document=None):
    return skin_capture.capture(session.engine, document or session.document, session.resources)


def reads(document, collector):
    return revisions(document, collector(document))


@pytest.mark.parametrize("values", [dict(fiber_radius=0.002), dict(gap_strength=0.5)])
def test_fiber_physical_settings_are_rejected_without_edits(session, values):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    before = session.document
    with pytest.raises(ValueError, match="topology FLOW only"):
        session.command("skin.contributor.configure", owner=fiber.id, values=values)
    assert session.document == before


def test_flow_round_trip_and_undo_preserve_fiber_and_bindings(session, tmp_path):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(flow=True))
    assert session.document.object(fiber.id) == fiber
    session.command("save", path=str(tmp_path / "fiber.anthroforge"), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(tmp_path / "fiber.anthroforge"))
    session.wait()
    assert skin_operations.settings_for(session.document.skin, fiber.id).flow
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(flow=False))
    session.command("undo")
    assert skin_operations.settings_for(session.document.skin, fiber.id).flow


def test_mirrored_fibers_are_not_physical_skin_sources(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.command("mirror.configure", target=bone, enabled=True)
    session.wait()
    captured = capture(session)
    assert all(row.identity.owner != fiber.id for row in captured.sources)
    assert not len(captured.geometry.segments)


def test_flow_edits_leave_envelope_provenance_and_geometry_unchanged(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    before = session.document
    captured = capture(session, before)
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(flow=True))
    after = session.document
    assert reads(before, skin_inputs.envelope) == reads(after, skin_inputs.envelope)
    assert reads(before, skin_inputs.construction) != reads(after, skin_inputs.construction)
    np.testing.assert_array_equal(captured.geometry.vertices, capture(session).geometry.vertices)
    assert all(read.owner != fiber.id for read in reads(after, skin_inputs.envelope))


def test_open_fiber_flow_path_remains_available_to_topology(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(flow=True))
    token = NativeCancellation(session.engine)
    result = skin_topology_capture.capture(
        session.engine, session.document, session.resources, token
    )
    assert not result.warnings and len(result.sources) == 1
    assert result.sources[0].identity.owner == fiber.id and len(result.data.points)
    assert fiber.id not in {row.identity.owner for row in capture(session).sources}


def test_prerelease_radius_is_read_but_never_written_or_used():
    payload = asdict(Skin())
    payload["contributors"] = [dict(owner="fiber", flow=True, fiber_radius=0.002)]
    restored = skin_codec.decode(payload)
    assert restored.contributors[0].flow
    assert "fiber_radius" not in asdict(restored)["contributors"][0]
