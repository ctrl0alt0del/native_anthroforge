"""Active scheduling, historical metadata and execution ownership have separate lifetimes."""

import weakref
from dataclasses import replace
from threading import Event

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port


def quick_job():
    return Job(
        "Cheap",
        frozenset({"owner"}),
        lambda d: d.revision,
        lambda revision, cancel: revision,
        lambda result: None,
        kind="attachments",
        interactive=True,
    )


class UnscannableHistory(list):
    def __iter__(self):
        raise AssertionError("Scheduling must never traverse completed history")


def test_completed_history_is_not_a_scheduling_input():
    scheduler = TaskCoordinator(Document)
    job = quick_job()
    scheduler.submit(job)
    assert not job.active
    scheduler.registry.history = UnscannableHistory(scheduler.jobs)
    scheduler.tick()
    scheduler.invalidate({"owner"})
    scheduler.invalidate_ports({Port("owner", "geometry")})
    scheduler.cancel_job(job.id)
    scheduler.restore(set())
    assert scheduler.queued() == [] and not scheduler.blocked
    scheduler.close()


def test_terminal_job_releases_execution_payload_but_keeps_diagnostics():
    scheduler = TaskCoordinator(lambda: Document(revision=12))
    job = quick_job()
    cancellation = weakref.ref(job.cancel)
    prepare = weakref.ref(job.prepare)
    scheduler.submit(job)
    assert job.state == "succeeded" and job.dispatch_revision == 12
    assert job.snapshot is None and job.future is None and job.cancel is None
    assert prepare() is None and cancellation() is None
    assert job.describe()["outputs"] == ["owner"] and job.assessment is not None
    assert all(not index for index in scheduler.registry.indexes.values())
    scheduler.close()


def test_restore_keeps_restart_recipe_after_retirement():
    document = Document(revision=7)
    scheduler = TaskCoordinator(lambda: document)
    job = quick_job()
    scheduler.can_publish = lambda job: False
    job.retry, job.restart_on_redo = lambda: "restarted", True
    scheduler.submit(job)
    document = replace(document, revision=8)
    restarts = scheduler.restore({0})
    assert job.state == "obsolete" and job.retry is None
    assert restarts[0].revision == 7 and restarts[0].callback() == "restarted"
    assert not scheduler.active_jobs
    scheduler.close()


def test_port_indexes_preserve_precise_invalidation_and_legacy_jobs():
    scheduler = TaskCoordinator(Document)
    scheduler.can_publish = lambda job: False
    a, b, legacy = quick_job(), quick_job(), quick_job()
    a.observes, b.observes = (
        frozenset({Port("owner", "pose")}),
        frozenset({Port("owner", "geometry")}),
    )
    for job in (a, b, legacy):
        scheduler.submit(job)
    scheduler.invalidate_ports({Port("owner", "geometry")})
    assert a.active and not b.active and not legacy.active
    assert scheduler.active_jobs == (a,)
    scheduler.close()


def test_failed_job_retains_retry_without_execution_snapshot():
    scheduler = TaskCoordinator(Document)
    job = quick_job()
    job.execute = lambda doc, cancel: 1 / 0
    job.retry = lambda: "retry"
    scheduler.submit(job)
    assert job.state == "failed" and job.retryable
    assert scheduler.retry(job.id) == "retry" and job.snapshot is None
    scheduler.close()


def test_cleanup_failure_retires_job_once_and_does_not_block():
    scheduler = TaskCoordinator(Document)
    job = quick_job()
    job.cleanup = lambda state: 1 / 0
    scheduler.submit(job)
    assert job.state == "failed" and not scheduler.active_jobs
    assert len(scheduler.errors) == 1 and job.cancel is None
    scheduler.close()


def test_close_releases_cancelled_worker_when_publication_is_blocked():
    scheduler = TaskCoordinator(Document)
    gate = Event()
    job = quick_job()
    job.kind = "generic"
    job.execute = lambda d, cancel: gate.wait(1)
    scheduler.can_publish = lambda job: False
    scheduler.submit(job)
    scheduler.tick()
    assert job.future is not None
    gate.set()
    scheduler.close()
    assert job.state == "cancelled" and not scheduler.active_jobs
    assert job.future is None and job.cancel is None
