from dataclasses import replace
from threading import Event, get_ident
from time import sleep
from types import SimpleNamespace

import pytest

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.application.task_schedulers import MeasuredTaskScheduler
from anthroforge.application.task_workloads import project_save
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import Schedule, Workload


@pytest.fixture
def coordinated():
    now, state, published = [0.0], [Document()], []
    coordinator = TaskCoordinator(lambda: state[0], clock=lambda: now[0])
    yield coordinator, now, state, published
    coordinator.close()


def attachment_job(published, entities=2, output="child"):
    return Job(
        "Attachment fixture",
        frozenset((output,)),
        lambda doc: doc,
        lambda doc, cancel: (doc.revision, get_ident()),
        published.append,
        kind="attachments",
        interactive=True,
        key="attachments:" + output,
        workload=lambda doc: Workload(entities=entities, affected=entities),
    )


def test_small_update_finishes_on_owner_thread_without_a_tick(coordinated):
    coordinator, _, _, published = coordinated
    job = attachment_job(published)
    coordinator.submit(job)
    assert published == [(0, get_ident())]
    assert job.execution == "inline" and job.state == "succeeded"
    assert not coordinator.blocked


def test_expensive_update_waits_then_captures_fresh_inputs(coordinated):
    coordinator, now, state, published = coordinated
    job = attachment_job(published, 500)
    coordinator.submit(job)
    assert coordinator.blocked and job.snapshot is None
    now[0] = job.ready_at - 0.001
    coordinator.tick()
    assert job.snapshot is None
    state[0] = replace(state[0], revision=7)
    now[0] = job.ready_at
    coordinator.wait(timeout=2)
    assert job.execution == "worker" and published[0][0] == 7
    assert published[0][1] != get_ident()


def test_repeated_requests_have_a_bounded_coalescing_deadline(coordinated):
    coordinator, now, _, published = coordinated
    for i in range(20):
        now[0] = i * 0.009
        job = attachment_job(published, 500)
        coordinator.submit(job)
    assert job.queued_since == 0.0 and job.ready_at <= 0.1
    assert sum(j.active for j in coordinator.jobs) == 1
    coordinator.wait(timeout=2)
    assert len(published) == 1


def test_reassess_before_execution_rejects_newly_expensive_inline_work(coordinated):
    coordinator, _, state, published = coordinated
    coordinator.inline_budget.spent_ms = 2
    job = attachment_job(published)
    job.workload = lambda doc: Workload(entities=2 if doc.revision == 0 else 1000)
    coordinator.submit(job)
    state[0] = replace(state[0], revision=1)
    coordinator.inline_budget.spent_ms = 0
    coordinator.wait(timeout=2)
    assert job.execution == "worker" and published[0][0] == 1


def slow_fixture(document, cancel):
    sleep(0.005)
    return document.revision


def test_measured_overrun_demotes_subsequent_similar_tasks(coordinated):
    coordinator, now, _, published = coordinated
    first = attachment_job(published)
    first.execute = slow_fixture
    coordinator.submit(first)
    now[0] = 0.02
    second = attachment_job(published)
    coordinator.submit(second)
    assert first.execution == "inline" and first.compute_ms >= 4
    assert second.assessment.schedule.execution == "worker"
    assert second.ready_at > now[0] and second.snapshot is None


def test_inline_budget_is_shared_between_independent_objects(coordinated):
    coordinator, now, _, published = coordinated
    coordinator.inline_budget.spent_ms = 1.99
    job = attachment_job(published)
    coordinator.submit(job)
    assert job.snapshot is None and coordinator.blocked
    now[0] = 0.016
    coordinator.tick()
    assert job.state == "succeeded" and job.execution == "inline"


def test_exhausted_budget_uses_worker_with_explanation(coordinated):
    coordinator, _, _, published = coordinated
    coordinator.inline_budget.spent_ms = 2
    job = attachment_job(published)
    coordinator.submit(job)
    coordinator.wait(timeout=2)
    assert job.execution == "worker"
    assert job.scheduling_details()["reason"] == "Shared interactive budget exhausted"


def gated_writer(gate):
    return Job(
        "Busy",
        frozenset(("child",)),
        lambda doc: doc,
        lambda doc, cancel: gate.wait(1),
        lambda result: None,
    )


def test_inline_update_never_bypasses_an_overlapping_writer(coordinated):
    coordinator, _, _, published = coordinated
    gate = Event()
    busy = gated_writer(gate)
    coordinator.submit(busy)
    coordinator.tick()
    job = attachment_job(published)
    coordinator.submit(job)
    assert job.snapshot is None and published == []
    gate.set()
    coordinator.wait(timeout=2)
    assert len(published) == 1


@pytest.mark.parametrize("kind", ["mesh_import", "project_open", "project_save"])
def test_explicit_file_operations_have_no_artificial_delay(coordinated, kind):
    coordinator, _, _, published = coordinated
    job = attachment_job(published)
    job.kind = kind
    job.workload = lambda doc: Workload(bytes=10**9)
    coordinator.submit(job)
    assert job.assessment.schedule.delay_ms == 0 and job.snapshot is None
    coordinator.wait(timeout=2)
    assert job.execution == "worker"


def test_unregistered_task_type_fails_before_admission(coordinated):
    coordinator, _, _, published = coordinated
    job = attachment_job(published)
    job.kind = "missing"
    with pytest.raises(ValueError, match="No task scheduler"):
        coordinator.submit(job)
    assert not coordinator.jobs and not coordinator.blocked


def test_large_surface_recapture_stays_background(coordinated):
    coordinator, _, _, published = coordinated
    job = attachment_job(published)
    job.workload = lambda doc: Workload(entities=2, recaptures=1, candidates=10000, triangles=20000)
    coordinator.submit(job)
    assert job.assessment.schedule.execution == "worker" and job.snapshot is None
    assert coordinator.blocked and published == []


def test_inline_eligibility_does_not_bypass_publication_gate(coordinated):
    coordinator, _, _, published = coordinated
    coordinator.can_publish = lambda job: False
    job = attachment_job(published)
    coordinator.submit(job)
    coordinator.tick()
    job.future.result(timeout=2)
    coordinator.tick()
    assert published == [] and coordinator.blocked
    coordinator.can_publish = lambda job: True
    coordinator.tick()
    assert len(published) == 1 and not coordinator.blocked


def test_save_estimate_counts_only_the_snapshot_assets():
    document = Document(entities=(SCP("Root", asset="used"),))
    small = SimpleNamespace(mesh=SimpleNamespace(counts=(8, 6, 24, 12, 1)))
    unused = SimpleNamespace(mesh=SimpleNamespace(counts=(100000, 100000, 300000, 100000, 7)))
    from anthroforge.application.resources import Resources

    estimate = project_save(Resources(meshes={"used": small, "unused": unused}), document)
    assert estimate.entities == 1 and estimate.bytes == 440


def test_live_parent_and_child_commit_together_and_undo(assembly, session):
    root, child = assembly
    session.command("begin")
    session.command("scp.transform", entity=root, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    assert session.document.entity(child).matrix[11] == pytest.approx(2)
    assert session.scheduler.jobs[-1].execution == "inline"
    assert not session.scheduler.blocked
    session.command("commit")
    session.command("undo")
    assert session.document.entity(child).matrix[11] == pytest.approx(0)
    session.command("redo")
    assert session.document.entity(child).matrix[11] == pytest.approx(2)


class DelayedAttachments(MeasuredTaskScheduler):
    def plan(self, workload, interactive):
        return Schedule("worker", 20, 50, 100, "Delayed fixture")


def test_edit_invalidation_preserves_first_pending_deadline(assembly, session):
    root, child = assembly
    now = [0.0]
    session.scheduler.clock = lambda: now[0]
    session.scheduler.task_schedulers["attachments"] = DelayedAttachments()
    for i in range(20):
        now[0] = i * 0.009
        session.command("scp.transform", entity=root, values=[0, 0, i, 0, 0, 0, 1, 1, 1])
    job = session.scheduler.jobs[-1]
    assert job.queued_since == 0.0 and job.ready_at <= 0.1
    session.command("wait", timeout=2)
    assert session.document.entity(child).matrix[11] == pytest.approx(19)


def test_delayed_writers_keep_save_blocked_and_undo_removes_them(assembly, session, tmp_path):
    root, _ = assembly
    session.scheduler.clock = lambda: 0.0
    session.scheduler.task_schedulers["attachments"] = DelayedAttachments()
    session.command("scp.transform", entity=root, values=[0, 0, 2, 0, 0, 0, 1, 1, 1])
    job = session.scheduler.jobs[-1]
    result = session.command("save", path=str(tmp_path / "pending.af"), blocked_policy="pending")
    assert result["status"] == "pending" and job.snapshot is None
    session.command("undo")
    assert not job.active and not session.scheduler.blocked
