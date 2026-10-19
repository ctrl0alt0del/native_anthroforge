from dataclasses import replace
from threading import Event
from time import monotonic, sleep

import pytest

from anthroforge.application.scheduler import Scheduler
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job, ObsoleteInputs


def controlled(label, output, gate, published):
    def compute(document, cancel):
        while not gate.wait(0.002):
            if cancel.is_set():
                return document.revision
        return document.revision

    return Job(label, frozenset((output,)), lambda doc: doc, compute, published.append)


def pump(scheduler, predicate):
    deadline = monotonic() + 3
    while not predicate():
        scheduler.tick()
        assert monotonic() < deadline
        sleep(0.002)


def stale_publication(value):
    raise ObsoleteInputs("Read set advanced while the worker ran.")


def test_publication_read_conflict_restarts_without_reporting_numerical_failure(state_scheduler):
    _, scheduler, published = state_scheduler
    gate = Event()
    gate.set()
    stale = controlled("stale", "a", gate, [])
    stale.publish = stale_publication
    fresh = controlled("fresh", "a", gate, published)
    stale.retry = lambda: scheduler.submit(fresh)
    stale.restart_on_input_change = True
    scheduler.submit(stale)
    scheduler.wait(3)
    assert stale.state == "obsolete" and fresh.state == "succeeded"
    assert published == [0] and not scheduler.errors


@pytest.fixture
def state_scheduler():
    state, published = [Document()], []
    scheduler = Scheduler(lambda: state[0])
    yield state, scheduler, published
    scheduler.close()


def test_checkpoint_advances_to_earliest_remaining_job_start(state_scheduler):
    state, scheduler, published = state_scheduler
    a, b = Event(), Event()
    first = controlled("first", "a", a, published)
    scheduler.submit(first)
    scheduler.tick()
    state[0] = replace(state[0], revision=1)
    second = controlled("second", "b", b, published)
    scheduler.submit(second)
    scheduler.tick()
    assert scheduler.checkpoint.revision == 0
    a.set()
    pump(scheduler, lambda: not first.active)
    assert second.active and scheduler.checkpoint.revision == 1
    b.set()


def test_same_output_serializes_and_captures_at_dispatch(state_scheduler):
    state, scheduler, published = state_scheduler
    a, b = Event(), Event()
    first = controlled("first", "a", a, published)
    second = controlled("second", "a", b, published)
    scheduler.submit(first)
    scheduler.submit(second)
    scheduler.tick()
    assert second.snapshot is None
    state[0] = replace(state[0], revision=3)
    a.set()
    pump(scheduler, lambda: second.snapshot is not None)
    assert second.snapshot.revision == 3
    b.set()
    scheduler.wait()


def test_obsolete_result_never_publishes():
    scheduler = Scheduler(Document)
    gate, published = Event(), []
    job = controlled("old", "a", gate, published)
    scheduler.submit(job)
    scheduler.tick()
    scheduler.invalidate({"a"})
    assert scheduler.blocked
    gate.set()
    scheduler.wait()
    assert published == [] and job.state == "obsolete"
    scheduler.close()


def fail(document, cancel):
    raise ValueError("Expected fixture failure")


def test_failure_is_terminal_and_does_not_block_commit():
    scheduler = Scheduler(Document)
    job = Job("failure", frozenset(("a",)), lambda doc: doc, fail, lambda result: None)
    scheduler.submit(job)
    scheduler.wait()
    assert job.state == "failed" and not scheduler.blocked
    scheduler.close()


def test_readonly_work_never_blocks_saving():
    scheduler = Scheduler(Document)
    gate, published = Event(), []
    job = controlled("read", "a", gate, published)
    job.writes = False
    scheduler.submit(job)
    scheduler.tick()
    assert not scheduler.blocked
    gate.set()
    scheduler.wait()
    scheduler.close()
