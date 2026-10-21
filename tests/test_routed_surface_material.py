"""Real routed fibers retain exact surfaces and anatomical material bindings."""

import numpy as np
import pytest

from tests import routed_surface_scene as scene
from tests.test_tissue_workflow import roundtrip


def attached_exact_surface(session):
    objects = scene.create(session)
    target = session.command("tissue.create", source=objects["exact"], preset="CUSTOM")
    session.wait()
    anchors = [scene.attachment(session, target, role) for role in ("TISSUE_BASE", "TISSUE_FINAL")]
    objects["attached"] = [session.document.object(key) for key in anchors]
    return objects


def assert_bindings_ready(session, captured):
    for before in captured:
        after = session.document.object(before.id)
        assert after.result.status == "ready", after.result.error
        assert after.binding == before.binding
        assert np.isfinite(after.resolved_frame).all()


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_exact_fiber_surface_bindings_survive_growth_shrink_and_reopen(session, tmp_path, backend):
    session.command("preferences.set", routing_backend=backend)
    objects = attached_exact_surface(session)
    scene.move(session, objects["supports"][-1], [0, 0, 0])
    assert_bindings_ready(session, objects["attached"])
    roundtrip(session, tmp_path / "adaptive-exact.anthroforge")
    scene.move(session, objects["supports"][-1], [0, 0, 3])
    assert_bindings_ready(session, objects["attached"])
    for before in objects["attached"]:
        after = session.document.object(before.id)
        np.testing.assert_allclose(after.resolved_frame, before.resolved_frame, atol=1e-8)
    assert not session.scheduler.errors


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_exact_fiber_surface_bindings_survive_undo_redo(session, backend):
    session.command("preferences.set", routing_backend=backend)
    objects = attached_exact_surface(session)
    scene.move(session, objects["supports"][-1], [0, 0, 0])
    assert_bindings_ready(session, objects["attached"])
    session.command("undo")
    session.wait()
    assert_bindings_ready(session, objects["attached"])
    session.command("redo")
    session.wait()
    assert_bindings_ready(session, objects["attached"])
