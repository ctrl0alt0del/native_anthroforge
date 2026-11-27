"""UI completion windows preserve atomic results, context fairness and shutdown cleanup."""

from threading import Event

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.core.document import Document
from tests.test_scheduler import controlled


def completed_jobs(coordinator, count, published):
    gate = Event()
    jobs = [controlled(str(i), str(i), gate, published) for i in range(count)]
    for job in jobs:
        coordinator.submit(job)
    coordinator.tick()
    gate.set()
    for job in jobs:
        job.future.result(timeout=3)
    return jobs


def test_publication_window_defers_next_result_after_atomic_overrun():
    clock, published = [0.0], []
    coordinator = TaskCoordinator(Document, workers=3, clock=lambda: clock[0])
    coordinator.publication_budget_ms = 2
    jobs = completed_jobs(coordinator, 3, published)
    for job in jobs:
        job.publish = lambda value: clock.__setitem__(0, clock[0] + 0.003)
    try:
        coordinator.tick()
        assert sum(job.state == "succeeded" for job in jobs) == 1
        coordinator.tick()
        assert sum(job.state == "succeeded" for job in jobs) == 2
    finally:
        coordinator.close()


def test_close_drains_every_completed_job_even_with_zero_publication_budget():
    coordinator = TaskCoordinator(Document, workers=3)
    coordinator.publication_budget_ms = 0
    jobs = completed_jobs(coordinator, 3, [])
    coordinator.close()
    assert not coordinator.all_active_jobs
    assert all(job.state == "cancelled" for job in jobs)


def test_budget_rotates_contexts_without_changing_publication_owner(session):
    session.wait(5)
    session.contexts.add("variant", session.document)
    coordinator, published = session.scheduler, []
    coordinator.publication_budget_ms = 0
    root = completed_jobs(coordinator, 2, published)
    with session.contexts.use("variant"):
        variant = completed_jobs(coordinator, 1, published)[0]
    coordinator.tick_cursor = 1
    coordinator.tick()
    assert variant.state == "succeeded"
    assert any(job.active for job in root)
    assert coordinator.context == ""
