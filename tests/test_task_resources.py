from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.application.task_resources import Admission
from anthroforge.application.task_schedulers import MeasuredTaskScheduler, SkinEnvelopeTaskScheduler
from anthroforge.core.document import Document
from anthroforge.core.scheduling import ResourceDemand, Schedule, Workload
from tests.test_scheduler import controlled, pump
from tests.test_task_coordination import attachment_job


class ResourceScheduler(MeasuredTaskScheduler):
    def plan(self, workload, interactive):
        return Schedule(resources=ResourceDemand(workload.candidates, workload.bytes))


@pytest.fixture
def setup():
    state, published = [Document()], []
    coordinator = TaskCoordinator(lambda: state[0])
    coordinator.admission = Admission(lambda: 4, lambda: 1000)
    coordinator.task_schedulers["generic"] = ResourceScheduler()
    yield coordinator, state, published
    coordinator.close()


def job(setup, name, threads=1, memory=0):
    coordinator, _, published = setup
    gate = Event()
    request = controlled(name, name, gate, published)
    request.workload = lambda doc: Workload(candidates=threads, bytes=memory)
    coordinator.submit(request)
    return request, gate


@pytest.mark.parametrize("threads,memory", [(4, 0), (0, 0), (1, 1200)])
def test_large_work_runs_alone_without_resource_rejection(setup, threads, memory):
    coordinator, state, published = setup
    first, gate = job(setup, "first", threads, memory)
    second, done = job(setup, "second")
    coordinator.tick()
    assert first.snapshot is not None and second.snapshot is None
    assert second.scheduling_details()["reason"].startswith("Waiting for")
    state[0] = replace(state[0], revision=7)
    gate.set()
    pump(coordinator, lambda: second.snapshot is not None)
    assert second.snapshot.revision == 7 and not second.execution_reason
    done.set()
    coordinator.wait(3)
    assert published == [0, 7] and not coordinator.errors


def test_available_capacity_runs_independent_jobs_together(setup):
    coordinator, _, _ = setup
    first, a = job(setup, "first", 2, 400)
    second, b = job(setup, "second", 2, 400)
    coordinator.tick()
    assert first.snapshot is not None and second.snapshot is not None
    a.set()
    b.set()
    coordinator.wait(3)


def test_waiting_job_can_be_cancelled_without_input_capture(setup):
    coordinator, _, _ = setup
    first, release = job(setup, "first", 0)
    second, _ = job(setup, "second")
    coordinator.tick()
    coordinator.cancel_job(second.id)
    assert second.snapshot is None and second.state == "cancelled"
    coordinator.cancel_job(first.id)
    coordinator.wait(3)
    third, done = job(setup, "third", 4)
    coordinator.tick()
    assert third.snapshot is not None
    done.set()


def test_reassessment_precedes_resource_admission_and_capture(setup):
    coordinator, state, _ = setup
    first, a = job(setup, "first", 2)
    second, b = job(setup, "second", 1)
    second.workload = lambda doc: Workload(candidates=1 if doc.revision == 0 else 4)
    state[0] = replace(state[0], revision=1)
    coordinator.tick()
    assert first.snapshot is not None and second.snapshot is None
    assert second.assessment.schedule.resources.threads == 4
    a.set()
    b.set()
    coordinator.wait(3)
    assert second.dispatch_revision == 1


def test_bounded_inline_edit_remains_available_during_heavy_work(setup):
    coordinator, _, published = setup
    _, release = job(setup, "heavy", 0)
    coordinator.tick()
    request = attachment_job(published, output="independent")
    coordinator.submit(request)
    assert request.execution == "inline" and request.state == "succeeded"
    release.set()


@pytest.mark.parametrize("threads,memory", [(-1, 0), (1, -1), (True, 0), (1.5, 0)])
def test_invalid_resource_estimates_are_rejected(threads, memory):
    with pytest.raises(ValueError):
        ResourceDemand(threads, memory)


def test_skin_envelope_reserves_its_native_team_before_input_capture(setup, monkeypatch):
    coordinator, _, _ = setup
    monkeypatch.setattr("anthroforge.application.worker_memory.budget", lambda: 0)
    coordinator.task_schedulers["skin_envelope"] = SkinEnvelopeTaskScheduler()
    running, release = job(setup, "running", 1)
    coordinator.tick()
    request = controlled("skin", "skin", Event(), [])
    request.kind = "skin_envelope"
    coordinator.submit(request)
    coordinator.tick()
    assert running.snapshot is not None and request.snapshot is None
    assert request.assessment.schedule.resources.threads == 4
    assert request.execution_reason == "Waiting for compute capacity"
    coordinator.cancel_job(request.id)
    release.set()
