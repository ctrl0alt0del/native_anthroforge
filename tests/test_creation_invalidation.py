"""Input edits cannot silently discard an asynchronous authored creation request."""

from threading import Event

import pytest

from anthroforge.application import fiber_tasks, surface_jobs
from anthroforge.core.fibers import Fiber
from anthroforge.core.surfaces import Surface
from tests.test_fiber_creation import scene
from tests.test_path_lifecycle import point
from tests.test_surface_workflow import curve


def hold(monkeypatch, module):
    original, entered, release = module.compute, Event(), Event()

    def compute(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(module, "compute", compute)
    return entered, release


def create(session, kind):
    if kind == "surface":
        a, b = curve(session), curve(session, 0.4)
        return a, lambda: session.command("surface.create", curves=[a, b]), Surface
    target, source = scene(session)
    item = session.document.object(source)
    bindings = [dict(point=p.id, target=target) for p in (item.points[0], item.points[-1])]
    return source, lambda: session.command("fiber.create", curve=source, bindings=bindings), Fiber


@pytest.mark.parametrize("kind", ["surface", "fiber"])
@pytest.mark.parametrize("running", [False, True])
def test_creation_survives_changed_inputs(session, monkeypatch, kind, running):
    source, request, cls = create(session, kind)
    entered, release = hold(monkeypatch, surface_jobs if kind == "surface" else fiber_tasks)
    request()
    if running:
        session.scheduler.tick()
        assert entered.wait(2)
    try:
        point(session, source, [-0.4, 0.1, 0.7])
    finally:
        release.set()
    session.wait(5)
    results = [item for item in session.document.objects if isinstance(item, cls)]
    assert len(results) == 1, [(j.kind, j.state, j.error) for j in session.scheduler.jobs]
    assert results[0].result.status == "ready"


@pytest.mark.parametrize("kind", ["surface", "fiber"])
def test_explicit_cancel_clears_pending_creation_restart(session, monkeypatch, kind):
    source, request, cls = create(session, kind)
    _, release = hold(monkeypatch, surface_jobs if kind == "surface" else fiber_tasks)
    job = request()
    try:
        point(session, source, [-0.4, 0.1, 0.7])
        session.command("job.cancel", job_id=job)
    finally:
        release.set()
    session.wait(5)
    assert not any(isinstance(item, cls) for item in session.document.objects)
    assert not session.scheduler.blocked


@pytest.mark.parametrize("kind", ["surface", "fiber"])
def test_undo_removes_creation_and_redo_restarts_once(session, monkeypatch, kind):
    _, request, cls = create(session, kind)
    _, release = hold(monkeypatch, surface_jobs if kind == "surface" else fiber_tasks)
    request()
    session.command("undo")
    release.set()
    session.wait(5)
    assert not any(isinstance(item, cls) for item in session.document.objects)
    session.command("redo")
    session.wait(5)
    assert len([item for item in session.document.objects if isinstance(item, cls)]) == 1


@pytest.mark.parametrize("kind", ["surface", "fiber"])
def test_deleted_creation_input_finishes_with_failure(session, monkeypatch, kind):
    source, request, cls = create(session, kind)
    _, release = hold(monkeypatch, surface_jobs if kind == "surface" else fiber_tasks)
    request()
    session.command("object.delete", target=source)
    release.set()
    session.wait(5)
    assert not session.scheduler.blocked
    assert not any(isinstance(item, cls) for item in session.document.objects)
    rows = session.command("issues.list", filters=dict(code="CALCULATION_FAILED"))["records"]
    assert rows


def test_fiber_history_does_not_accept_capture_from_later_parent_pose(session, monkeypatch):
    _, request, _ = create(session, "fiber")
    target = session.document.entities[0].id
    _, release = hold(monkeypatch, fiber_tasks)
    request()
    origin = session.history.cursor
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    release.set()
    session.wait(5)
    fiber = next(item for item in session.document.objects if isinstance(item, Fiber))
    old = session.history.entries[origin].document
    assert fiber.id not in old.registry.records
    session.command("undo")
    session.wait(5)
    assert session.document.object(fiber.id).result.status == "ready"
