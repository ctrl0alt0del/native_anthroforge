"""The new graph is one cancellable writer; history never receives future captured inputs."""

from threading import Event

from anthroforge.application import attached_creation_compute
from anthroforge.core.fibers import Fiber
from tests.test_attached_creation import surface_scene
from tests.test_fiber_creation import scene
from tests.test_surface_branches import branched


def blocked(monkeypatch):
    original, entered, release = attached_creation_compute.compute, Event(), Event()

    def compute(*args):
        entered.set()
        assert release.wait(5)
        return original(*args)

    monkeypatch.setattr(attached_creation_compute, "compute", compute)
    return entered, release


def start(session, monkeypatch):
    _, source, _ = surface_scene(session)
    before = session.document.objects
    entered, release = blocked(monkeypatch)
    result = session.command("tissue.create", source=source.id)
    session.scheduler.tick()
    assert entered.wait(5)
    assert session.document.objects == before
    return result, release, before


def test_cancel_discards_entire_graph(session, monkeypatch):
    result, release, before = start(session, monkeypatch)
    session.command("job.cancel", job_id=result["job_id"])
    release.set()
    session.wait()
    assert session.document.objects == before
    assert result["object_id"] not in session.document.registry.records
    session.resources.require(session.document)


def test_undo_running_creation_and_redo_restart(session, monkeypatch):
    result, release, before = start(session, monkeypatch)
    session.command("undo")
    release.set()
    session.wait()
    assert session.document.objects == before
    session.command("redo")
    session.wait()
    assert session.document.object(result["object_id"]).result.asset
    assert not session.scheduler.errors


def test_failure_leaves_no_converted_curves_or_surface(session, monkeypatch):
    def fail(*args):
        raise ValueError("Injected capture failure")

    _, source, _ = surface_scene(session)
    before = session.document.objects
    monkeypatch.setattr(attached_creation_compute, "surface", fail)
    result = session.command("membrane.create", source=source.id)
    session.wait()
    assert session.document.objects == before
    assert result["object_id"] not in session.document.registry.records
    assert any("Injected capture failure" in e for e in session.scheduler.errors)


def test_edit_during_capture_restarts_with_current_input(session, monkeypatch):
    _, source = scene(session)
    entered, release = blocked(monkeypatch)
    result = session.command("tissue.create", source=source)
    session.scheduler.tick()
    assert entered.wait(5)
    point = session.document.object(source).points[1].id
    session.command("curve.point.update", curve=source, point=point, position=[0, 0.3, 0.9])
    release.set()
    session.wait()
    item = session.document.object(result["object_id"])
    fiber = session.document.object(item.source)
    assert isinstance(fiber, Fiber) and fiber.points[1].position == (0, 0.3, 0.9)
    assert not session.scheduler.errors
    verify_historical_capture(session, result["object_id"])


def verify_historical_capture(session, identity):
    session.command("undo")
    session.wait()
    tissue = session.document.object(identity)
    fiber = session.document.object(tissue.source)
    assert fiber.points[1].position == (0, 0.25, 0.8)
    session.resources.require(session.document)


def test_source_graph_change_replans_without_orphaned_junctions(session, monkeypatch):
    scene(session)
    _, source, branch = branched(session)
    entered, release = blocked(monkeypatch)
    result = session.command("membrane.create", source=source)
    session.scheduler.tick()
    assert entered.wait(5)
    session.command("surface.branch.remove", target=source, branch=branch)
    release.set()
    session.wait()
    membrane = session.document.object(result["object_id"])
    assert membrane.kind == "LOFT" and len(membrane.curves) == 2
    assert not any(
        p.junction for u in membrane.curves for p in session.document.object(u.curve).points
    )
