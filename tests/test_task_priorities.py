"""Priority follows causal work and active prerequisites, never entity kinds."""

from threading import Event

import pytest

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from tests.test_scheduler import pump


@pytest.fixture
def queue():
    now = [0.0]
    coordinator = TaskCoordinator(Document, workers=1, clock=lambda: now[0])
    yield coordinator, now
    coordinator.close()


def task(label, priority=0, interactive=False):
    return Job(
        label,
        frozenset((label,)),
        lambda doc: doc,
        lambda doc, cancel: None,
        lambda result: None,
        priority=priority,
        interactive=interactive,
        provides=frozenset((Port(label, "value"),)),
    )


def submit(queue, *jobs):
    coordinator, now = queue
    for job in jobs:
        coordinator.submit(job)
        now[0] += 1


def needs(job, *providers):
    job.prerequisites = frozenset(Port(provider.label, "value") for provider in providers)
    return job


def labels(coordinator):
    return [job.label for job in coordinator.queued()]


def test_transitive_urgent_dependency_dispatches_before_older_medium_work(queue):
    coordinator, _ = queue
    medium, base = task("other", 50), task("base")
    middle, visible = task("mid"), task("view", 10, True)
    needs(middle, base)
    needs(visible, middle)
    submit(queue, medium, base, middle, visible)
    assert labels(coordinator)[:3] == ["base", "mid", "view"]
    coordinator.tick()
    assert base.started and not medium.started
    assert base.queue_demand.source == visible.id
    assert not base.interactive and base.priority == 0


def test_donation_is_withdrawn_when_consumer_is_cancelled(queue):
    coordinator, _ = queue
    other, base, consumer = task("other", 50), task("base"), task("consumer", 100)
    needs(consumer, base)
    submit(queue, other, base, consumer)
    assert labels(coordinator)[0] == "base"
    coordinator.cancel_job(consumer.id)
    assert labels(coordinator) == ["other", "base"]
    assert base.queue_demand.priority == 0


def test_dependency_cycles_terminate_ranking_without_unblocking_cycle(queue):
    coordinator, _ = queue
    first, second, other = task("first", 100), task("second"), task("other")
    needs(first, second)
    needs(second, first)
    submit(queue, first, second, other)
    coordinator.tick()
    assert other.started and not first.started and not second.started
    assert second.queue_demand.priority == 100


def test_followup_keeps_causal_age_urgency_but_its_own_workspace_priority(queue):
    coordinator, now = queue
    source, child = task("source", 10, True), task("outside")
    source.publish = lambda result: coordinator.submit(child)
    submit(queue, source)
    now[0] = 10
    coordinator.wait(2)
    assert child.urgency == source.urgency
    assert child.queue_demand.priority == 100 and source.queue_demand.priority == 110
    assert not child.interactive and child.queued_since == 10


def test_replacement_preserves_fifo_before_later_same_urgency_work(queue):
    coordinator, _ = queue
    first, later, replacement = task("first", 10, True), task("later", 10, True), task("new", 10)
    first.key = replacement.key = "logical-request"
    submit(queue, first, later, replacement)
    assert first.state == "obsolete"
    assert labels(coordinator) == ["new", "later"]
    assert replacement.queued_since == first.queued_since
    assert replacement.urgency == first.urgency and not replacement.interactive


def test_same_causal_age_uses_preserved_queue_age_not_new_job_creation(queue):
    coordinator, _ = queue
    root = task("root", 10, True)
    first, later, replacement = task("first", 10), task("later", 10), task("new", 10)
    first.key = replacement.key = "request"
    submit(queue, root)
    coordinator.priorities.call(root, submit, queue, first, later, replacement)
    assert labels(coordinator) == ["root", "new", "later"]


def test_cancelled_consumer_still_running_cannot_keep_donating(queue):
    coordinator, _ = queue
    gate, running = Event(), task("running", 100)
    running.execute = lambda doc, cancel: gate.wait(1)
    submit(queue, running)
    coordinator.tick()
    low, medium = task("low"), task("medium", 50)
    submit(queue, low, medium)
    coordinator.registry.update(running, lambda: needs(running, low))
    coordinator.cancel_job(running.id)
    assert labels(coordinator) == ["medium", "low"]
    assert coordinator.blocked
    gate.set()


def test_priority_does_not_preempt_running_writer_or_bypass_reservation(queue):
    coordinator, _ = queue
    gate, running, urgent = Event(), task("shared"), task("shared", 100)
    running.execute = lambda doc, cancel: gate.wait(1)
    submit(queue, running)
    coordinator.tick()
    submit(queue, urgent)
    coordinator.tick()
    assert not urgent.started and running.active
    gate.set()
    pump(coordinator, lambda: not running.active)
    coordinator.wait(2)
    assert urgent.started >= running.finished


def test_automatic_retry_inherits_intent_without_changing_execution_hint(queue):
    coordinator, _ = queue
    first, replacement = task("first", 10, True), task("replacement", 10)
    first.restart_on_input_change = True
    first.retry = lambda: coordinator.submit(replacement)
    submit(queue, first)
    coordinator.cancel_job(first.id, obsolete=True, restart=True)
    coordinator.wait(2)
    assert replacement.urgency == first.urgency and not replacement.interactive
    assert replacement.state == "succeeded"


def test_changed_prerequisites_withdraw_old_donation(queue):
    coordinator, _ = queue
    old, new, consumer = task("old"), task("new"), task("consumer", 100)
    needs(consumer, old)
    submit(queue, old, new, consumer)
    assert labels(coordinator)[0] == "old"
    coordinator.registry.update(consumer, lambda: needs(consumer, new))
    assert labels(coordinator)[0] == "new"
    assert old.queue_demand.priority == 0
