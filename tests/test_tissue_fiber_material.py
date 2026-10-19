"""Fibers keep role-specific material captures across tissue compaction, edits and history."""

import numpy as np
import pytest

from anthroforge.application.resources import referenced
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import Port
from tests.test_fiber_creation import path
from tests.test_fiber_editing import edited_point
from tests.test_tissue_anchor_material import bound_to_second_side
from tests.test_tissue_routing import fail_final
from tests.test_tissue_workflow import roundtrip


def fiber_on_tissue(session, role="TISSUE_FINAL"):
    tissue, anchor = bound_to_second_side(session)
    position = np.asarray(anchor.resolved_position)
    positions = [position + [x, 0, -0.02] for x in (-0.03, 0, 0.03)]
    curve = session.command("curve.create", points=[dict(position=p.tolist()) for p in positions])
    session.wait()
    points = session.document.object(curve).points
    bindings = [dict(point=p.id, target=tissue, role=role) for p in (points[0], points[-1])]
    session.command("fiber.create", curve=curve, bindings=bindings)
    session.wait()
    item = next(o for o in reversed(session.document.objects) if isinstance(o, Fiber))
    assert all(b.target == tissue for b in item.bindings), session.scheduler.errors
    return tissue, item


def test_fiber_retains_material_through_compaction_and_current_shape_edit(session, tmp_path):
    target, fiber = fiber_on_tissue(session)
    shape = path(session, fiber.id)
    session.command("tissue.inflation", target=target, side="a", changes=dict(enabled=False))
    session.wait()
    assert session.document.object(fiber.id).result.status == "ready"
    np.testing.assert_allclose(path(session, fiber.id), shape, atol=1e-9)
    position = path(session, fiber.id)[len(shape) // 2, :3] + [0, 0.01, -0.01]
    changed = edited_point(session, fiber.id, 1, position.tolist())
    assert changed.bindings == fiber.bindings
    np.testing.assert_allclose(path(session, fiber.id)[[0, -1], :3], shape[[0, -1], :3], atol=1e-9)
    validate_saved_captures(session, changed, tmp_path)


def validate_saved_captures(session, item, location):
    captures = {s.material_asset for s in item.supports}
    assert len(captures) >= 2
    assert captures.issubset(referenced(session.document)["meshes"])
    roundtrip(session, location / "tissue-fiber.anthroforge")
    assert session.document.object(item.id).bindings == item.bindings
    session.command(
        "tissue.inflation", target=item.bindings[0].target, side="b", changes=dict(amount=0.12)
    )
    session.wait()
    assert session.document.object(item.id).result.status == "ready"
    assert session.document.object(item.id).bindings == item.bindings


def test_selected_role_is_explicit_and_final_failure_retains_accepted_path(session, monkeypatch):
    target, fiber = fiber_on_tissue(session)
    shape = path(session, fiber.id)
    ports = session.document.index.structure.dependencies[Port(fiber.id, "path")]
    assert Port(target, "final") in ports and Port(target, "geometry") not in ports
    fail_final(monkeypatch, target)
    session.command("evaluate", entities=[target])
    session.wait()
    item = session.document.object(fiber.id)
    assert item.result.status == "failed" and "final" in item.result.error.lower()
    np.testing.assert_array_equal(path(session, fiber.id), shape)
    monkeypatch.undo()
    session.command("evaluate", entities=[target])
    session.wait()
    assert session.document.object(fiber.id).result.status == "ready"


def test_explicit_base_binding_does_not_follow_inflation(session):
    target, fiber = fiber_on_tissue(session, "TISSUE_BASE")
    shape = path(session, fiber.id)
    ports = session.document.index.structure.dependencies[Port(fiber.id, "path")]
    assert Port(target, "base") in ports
    assert all(b.role == "TISSUE_BASE" for b in fiber.bindings)
    session.command("tissue.inflation", target=target, side="b", changes=dict(amount=0.12))
    session.wait()
    np.testing.assert_allclose(path(session, fiber.id)[[0, -1], :3], shape[[0, -1], :3], atol=1e-9)
    reject_unavailable_role(session, fiber, target)


def reject_unavailable_role(session, fiber, target):
    with pytest.raises(ValueError, match="provide"):
        session.command(
            "fiber.binding.set",
            curve=fiber.id,
            point=fiber.points[0].id,
            target=target,
            role="SCP_GEOMETRY",
        )
