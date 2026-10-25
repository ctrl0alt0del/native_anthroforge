"""Selectable propagation preserves shared attachment, execution and lifetime contracts."""

from dataclasses import replace
from threading import Event

import numpy as np
import pytest

from anthroforge.application import attachment_assets, curve_evaluation, fiber_deformation
from anthroforge.application.path_tasks import make_job
from anthroforge.core.preferences import Preferences
from anthroforge.native.mesh import NativeCancellation
from tests.test_automatic_routing_lifecycle import dispatch
from tests.test_fiber_creation import bind, path, scene


@pytest.mark.parametrize("method", ["SMOOTH_SHAPE", "LOCAL_SURFACE"])
@pytest.mark.parametrize("closed", [False, True])
def test_nonidentity_capture_and_rigid_translation(session, method, closed):
    target, source = scene(session, closed)
    values = [1, 2, 3, 10, 20, 30, 1.4, 0.7, 1.2]
    session.command("scp.transform", entity=target, values=values)
    session.wait()
    fiber = bind(session, target, source)
    before = path(session, fiber.id)
    session.command("preferences.set", fiber_propagation=method)
    values[2] += 1
    session.command("scp.transform", entity=target, values=values)
    session.wait()
    assert session.document.object(fiber.id).result.status == "ready"
    np.testing.assert_allclose(path(session, fiber.id)[:, :3], before[:, :3] + [0, 0, 1], atol=1e-9)


def test_preference_changes_only_future_dispatch(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before, history = session.document, session.history.cursor
    job = make_job(session, fiber.id)
    session.command("preferences.set", fiber_propagation="LOCAL_SURFACE")
    assert session.document is before and session.history.cursor == history
    assert not session.scheduler.active_jobs
    assert job.prepare(session.document)[2].fiber_propagation == "LOCAL_SURFACE"
    with pytest.raises(ValueError, match="Fiber propagation"):
        session.command("preferences.set", fiber_propagation="UNKNOWN")
    assert Preferences().fiber_propagation == "SMOOTH_SHAPE"


def blocked_propagation(monkeypatch):
    original, gate, started, methods = fiber_deformation.resolve, Event(), Event(), []

    def blocked(*args):
        methods.append(args[-1])
        started.set()
        assert gate.wait(5)
        return original(*args)

    monkeypatch.setattr(fiber_deformation, "resolve", blocked)
    return gate, started, methods


def test_running_calculation_retains_its_method(session, monkeypatch):
    target, source = scene(session)
    fiber = bind(session, target, source)
    gate, started, methods = blocked_propagation(monkeypatch)
    try:
        dispatch(session, fiber.id)
        assert started.wait(2)
        session.command("preferences.set", fiber_propagation="LOCAL_SURFACE")
    finally:
        gate.set()
    session.wait()
    session.command("curve.evaluate", curve=fiber.id)
    session.wait()
    assert methods == ["SMOOTH_SHAPE", "LOCAL_SURFACE"]


def test_local_method_is_the_original_attachment_evaluator(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    asset = session.resources.attachments[fiber.attachment_asset]
    original = attachment_assets.resolved_points(
        session.engine, session.document, session.assets, asset, 0
    )
    actual = fiber_deformation.resolve(
        session.engine, session.document, session.resources, fiber, asset, 0, "LOCAL_SURFACE"
    )
    np.testing.assert_array_equal(actual, original)


def test_preparation_is_cached_bounded_and_cancellable(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    asset = session.resources.attachments[fiber.attachment_asset]
    first, _ = fiber_deformation.prepare(session.engine, session.resources, fiber, asset, 0)
    second, _ = fiber_deformation.prepare(session.engine, session.resources, fiber, asset, 0)
    assert first is second and first.bytes >= asset.field.bytes
    cache = session.engine.fiber_deformations
    cache.clear()
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        fiber_deformation.prepare(session.engine, session.resources, fiber, asset, cancel.handle)
    assert cache.bytes == 0


def legacy_project(session, file):
    target, source = scene(session)
    fiber = bind(session, target, source)
    asset = session.resources.attachments[fiber.attachment_asset]
    session.resources.attachments[fiber.attachment_asset] = replace(
        asset, field=replace(asset.field, frames=())
    )
    from anthroforge.application import storage

    storage.atomic_save(file, session.document, session.resources)
    return fiber


def test_legacy_capture_hints_do_not_change_saved_results(session, tmp_path):
    from anthroforge.application import storage

    file = tmp_path / "legacy.anthroforge"
    fiber = legacy_project(session, file)
    before = path(session, fiber.id)
    document, resources = storage.read_package(file, session.engine)
    assert resources.attachments[fiber.attachment_asset].field.frame_hints
    np.testing.assert_array_equal(resources.paths[fiber.result.asset].path.array(), before)
    evaluated = curve_evaluation.evaluate(session.engine, document, resources, fiber.id, 0)
    np.testing.assert_allclose(evaluated.asset.path.array(), before, atol=1e-9)


@pytest.mark.parametrize("closed", [False, True])
def test_dense_curve_preparation_preserves_neutral_shape(session, closed):
    target, source = scene(session, closed)
    session.command("curve.edit", curve=source, resolution=300)
    session.wait()
    fiber = bind(session, target, source)
    before = path(session, fiber.id)
    assert len(before) > 512
    session.command("curve.evaluate", curve=fiber.id)
    session.wait()
    assert session.document.object(fiber.id).result.status == "ready"
    np.testing.assert_allclose(path(session, fiber.id)[:, :3], before[:, :3], atol=1e-9)
