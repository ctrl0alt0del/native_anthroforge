"""Shared transform policy and accepted creation selection across desktop/API boundaries."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.application import fiber_tasks
from anthroforge.core.fibers import Fiber
from anthroforge.desktop.controller import Controller
from tests.test_creation_invalidation import hold
from tests.test_fiber_creation import bind, scene

DELTAS = ([1, 0, 0, 0, 0, 0, 1, 1, 1], [0, 0, 0, 0, 20, 0, 1, 1, 1], [0, 0, 0, 0, 0, 0, 2, 2, 2])


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    yield value
    value.close()
    assert app


@pytest.mark.parametrize("values", DELTAS)
@pytest.mark.parametrize("world", [False, True])
def test_fiber_object_transform_is_rejected_without_history_or_jobs(session, values, world):
    target, source = scene(session)
    fiber = bind(session, target, source)
    before, cursor, jobs = session.document, session.history.cursor, len(session.scheduler.jobs)
    with pytest.raises(ValueError, match="Fibers follow anatomical bindings"):
        session.command("object.transform", target=fiber.id, values=values, world=world)
    assert session.document == before and session.history.cursor == cursor
    assert len(session.scheduler.jobs) == jobs and session.history.before is None
    session.command("object.transform", target=source, values=values, world=world)
    session.wait()
    assert session.document.object(source).matrix != before.object(source).matrix


def setup_creation(controller):
    target, source = scene(controller.session)
    controller.refresh()
    controller.select(source)
    controller.authoring.setEditing(True)
    points = controller.session.document.object(source).points
    bindings = [dict(point=p.id, target=target) for p in (points[0], points[-1])]
    return dict(curve=source, bindings=bindings)


def settle(controller):
    controller.session.wait(5)
    controller.refresh()


def assert_source_context(controller, source):
    assert controller.selection == source and controller.authoring.editing
    assert controller.creation_selection.pending is None
    assert controller.session.history.before is None


def test_accepted_creation_exits_editing_selects_fiber_and_keeps_one_undo(controller):
    arguments = setup_creation(controller)
    session, cursor = controller.session, controller.session.history.cursor
    controller.createConstruction("fiber.create", arguments)
    settle(controller)
    fiber = session.document.object(controller.selection)
    assert isinstance(fiber, Fiber) and not controller.authoring.active
    assert not controller.selectedData["transformable"] and session.history.cursor == cursor + 1
    assert not controller.authoring.selection and controller.creation_selection.pending is None
    controller.run("undo", {})
    assert fiber.id not in session.document.registry.records
    controller.run("redo", {})
    settle(controller)
    assert isinstance(session.document.object(fiber.id), Fiber)


def test_rejected_creation_preserves_source_edit_context(controller):
    arguments = setup_creation(controller)
    arguments["bindings"] = []
    assert controller.createConstruction("fiber.create", arguments) is None
    assert_source_context(controller, arguments["curve"])


def test_cancelled_creation_does_not_select_a_missing_fiber(controller, monkeypatch):
    arguments = setup_creation(controller)
    _, release = hold(monkeypatch, fiber_tasks)
    job = controller.createConstruction("fiber.create", arguments)
    controller.run("job.cancel", dict(job_id=job))
    release.set()
    settle(controller)
    assert_source_context(controller, arguments["curve"])
    assert not any(isinstance(o, Fiber) for o in controller.session.document.objects)


def fail_capture(*args):
    raise ValueError("Capture failed for test")


def test_failed_capture_does_not_exit_editing(controller, monkeypatch):
    arguments = setup_creation(controller)
    monkeypatch.setattr(fiber_tasks, "compute", fail_capture)
    job = controller.createConstruction("fiber.create", arguments)
    settle(controller)
    assert controller.session.scheduler.registry.by_id[job].state == "failed"
    assert_source_context(controller, arguments["curve"])


@pytest.mark.parametrize("change", ["selection", "editing", "undo"])
def test_pending_creation_does_not_steal_a_new_context(controller, monkeypatch, change):
    arguments = setup_creation(controller)
    _, release = hold(monkeypatch, fiber_tasks)
    controller.createConstruction("fiber.create", arguments)
    if change == "selection":
        controller.select(controller.session.document.entities[0].id)
    elif change == "editing":
        controller.authoring.setEditing(False)
    else:
        controller.run("undo", {})
    expected = controller.selection, controller.authoring.editing
    release.set()
    settle(controller)
    assert (controller.selection, controller.authoring.editing) == expected
    assert controller.creation_selection.pending is None


def test_superseded_capture_still_selects_its_accepted_fiber(controller, monkeypatch):
    arguments = setup_creation(controller)
    _, release = hold(monkeypatch, fiber_tasks)
    controller.createConstruction("fiber.create", arguments)
    item = controller.session.document.object(arguments["curve"])
    controller.run(
        "curve.point.update", dict(curve=item.id, point=item.points[1].id, position=[0, 0.4, 0.8])
    )
    release.set()
    settle(controller)
    assert isinstance(controller.session.document.object(controller.selection), Fiber)
    assert not controller.authoring.active and controller.creation_selection.pending is None


def test_controller_rejects_whole_fiber_gestures_but_allows_components(controller):
    arguments = setup_creation(controller)
    controller.createConstruction("fiber.create", arguments)
    settle(controller)
    for mode in ("Move", "Rotate", "Scale"):
        assert not controller.beginTransform(mode)
        assert controller.session.history.before is None
    controller.authoring.setEditing(True)
    point = next(row for row in controller.authoring.componentRows if row["part"] == "position")
    controller.authoring.selectComponent(point["key"], False)
    for mode in ("Move", "Rotate", "Scale"):
        assert controller.beginTransform(mode)
        controller.endTransform(True)
