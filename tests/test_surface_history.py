"""Asynchronous live-reference creation never installs future-input geometry into history."""

from anthroforge.application.task_schedulers import CurvePathTaskScheduler
from anthroforge.core.scheduling import Schedule
from anthroforge.core.surfaces import Surface
from tests.test_path_lifecycle import blocked_paths, point
from tests.test_surface_workflow import curve


def deferred_creation(session, monkeypatch):
    a, b = curve(session), curve(session, 0.4)
    monkeypatch.setattr(CurvePathTaskScheduler, "plan", lambda *args: Schedule("worker"))
    gate = blocked_paths(monkeypatch)
    point(session, a, [0, 0, 0.2])
    session.command("surface.create", curves=[a, b])
    origin = session.history.cursor
    session.command("object.rename", target=b, name="Later rename")
    gate.set()
    session.wait()
    target = next(o.id for o in session.document.objects if isinstance(o, Surface))
    return a, target, origin


def test_historical_creation_has_no_geometry_from_a_future_input_revision(session, monkeypatch):
    a, target, origin = deferred_creation(session, monkeypatch)
    current = session.document.object(target)
    old = session.history.entries[origin].document
    assert current.result.status == "ready"
    assert old.object(a).result.status == "pending"
    earlier = old.object(target)
    assert earlier.result.status == "pending" and not earlier.result.asset
    session.command("undo")
    session.wait()
    assert session.document.object(target).result.status == "ready"
