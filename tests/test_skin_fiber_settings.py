"""Skin radius is authored contributor data, with shared undo/persistence and mirror reuse."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import skin_capture, skin_operations
from anthroforge.core.skin import SkinStage
from tests.test_fiber_creation import bind, scene


def test_radius_edit_does_not_change_path_or_attachment_and_marks_rebuild(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.replace_document(skin=replace(session.document.skin, topology=SkinStage(asset="prior")))
    before = session.document
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(fiber_radius=0.002))
    assert session.document.object(fiber.id) == fiber
    assert session.document.skin.construction_stale
    assert skin_operations.settings_for(session.document.skin, fiber.id).fiber_radius == 0.002
    session.command("undo")
    assert session.document == before


def test_radius_round_trip_and_scope_validation(session, tmp_path):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.command("skin.contributor.configure", owner=fiber.id, values=dict(fiber_radius=0.002))
    session.command("save", path=str(tmp_path / "fiber.anthroforge"), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(tmp_path / "fiber.anthroforge"))
    session.wait()
    assert skin_operations.settings_for(session.document.skin, fiber.id).fiber_radius == 0.002
    with pytest.raises(ValueError, match="require a Fiber"):
        session.command("skin.contributor.configure", owner=bone, values=dict(fiber_radius=0.002))


def test_mirror_reuses_exact_source_tube(session):
    bone, curve = scene(session)
    fiber = bind(session, bone, curve)
    session.command("mirror.configure", target=bone, enabled=True)
    session.wait()
    captured = skin_capture.capture(session.engine, session.document, session.resources)
    rows = [row for row in captured.sources if row.identity.owner == fiber.id]
    assert len(rows) == 2 and rows[0].mesh is rows[1].mesh
    assert rows[0].frame != rows[1].frame
    assert not len(captured.geometry.segments)
    np.testing.assert_array_equal(rows[0].mesh.array(0), rows[1].mesh.array(0))
