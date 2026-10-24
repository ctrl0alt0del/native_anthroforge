"""Retained-position rebinding and material-normal edits share normal curve transactions."""

import numpy as np
import pytest

from anthroforge.application import surface_providers
from tests.test_fiber_creation import bind, path, scene


def pin_goal(session, binding, value):
    record = list(binding.attachment.binding)
    record[17] = value
    provider = surface_providers.get(
        session.engine, session.document, session.assets, binding.reference
    )
    frame = surface_providers.binding_frames(
        provider, session.assets, binding.material_asset, [record], 0
    )
    return frame.reshape(4, 4)[:3, 3]


def test_normal_offset_moves_pin_without_changing_material_reference(session):
    fiber = bind(session, *scene(session))
    binding, before = fiber.bindings[0], path(session, fiber.id)
    expected = pin_goal(session, binding, 0.12)
    session.command("fiber.binding.offset", curve=fiber.id, point=binding.point, value=0.12)
    session.wait()
    assert not session.scheduler.errors
    current = session.document.object(fiber.id)
    assert current.bindings[0].attachment.binding[:15] == binding.attachment.binding[:15]
    assert current.bindings[0].attachment.binding[17] == pytest.approx(0.12)
    np.testing.assert_allclose(path(session, fiber.id)[0, :3], expected, atol=1e-8)
    session.command("undo")
    np.testing.assert_array_equal(path(session, fiber.id), before)


def test_rebind_all_keeps_shape_targets_and_one_undo(session):
    fiber = bind(session, *scene(session))
    before, count = path(session, fiber.id), len(session.history.entries)
    session.command("fiber.rebind", curve=fiber.id)
    session.wait()
    assert not session.scheduler.errors
    current = session.document.object(fiber.id)
    np.testing.assert_allclose(path(session, fiber.id), before, atol=1e-10)
    assert [b.reference for b in current.bindings] == [b.reference for b in fiber.bindings]
    assert len(session.history.entries) == count + 1


def test_manual_offset_intent_roundtrips_before_evaluation(session, tmp_path):
    fiber = bind(session, *scene(session))
    session.command("update_mode", entity=fiber.id, mode="MANUAL")
    session.command(
        "fiber.binding.offset", curve=fiber.id, point=fiber.bindings[0].point, value=0.2
    )
    saved = tmp_path / "pending.anthroforge"
    session.command("save", path=str(saved), blocked_policy="wait")
    session.command("open", path=str(saved))
    assert session.document.object(fiber.id).edit.offsets == (fiber.bindings[0].point,)
    session.command("evaluate", entities=[fiber.id])
    session.wait()
    assert not session.scheduler.errors
    actual = session.document.object(fiber.id).bindings[0].attachment.binding[17]
    assert actual == pytest.approx(0.2)
