"""Cancelled explicit remediation retains the original, retryable failure evidence."""

from functools import partial
from threading import Event

from anthroforge.core.jobs import Job
from tests.test_issue_integration import records


def compute(gate, broken, document, cancel):
    if broken:
        raise RuntimeError("Original calculation failure")
    gate.wait(2)
    return "recovered"


def submit(session, gate, published, broken=False):
    job = Job(
        "Retry fixture",
        frozenset(),
        lambda d: d,
        partial(compute, gate, broken),
        published.append,
        key="retry-fixture",
    )
    job.retry = partial(submit, session, gate, published)
    session.scheduler.submit(job)
    return job


def initial_failure(session, gate, published):
    submit(session, gate, published, broken=True)
    session.wait(5)
    return records(session, provider="tasks.v1")[0]


def test_cancelled_retry_preserves_failure_and_next_retry_can_finish(session):
    gate, published = Event(), []
    row = initial_failure(session, gate, published)
    session.command("issues.fix", identity=row["id"], name="retry")
    session.command("issues.cancel_fix", identity=row["id"])
    gate.set()
    session.wait(5)
    assert session.command("issues.repairs")[-1]["state"] == "CANCELLED"
    assert records(session, provider="tasks.v1")[0]["freshness"] == "current"
    assert not published
    session.command("issues.fix", identity=row["id"], name="retry")
    session.wait(5)
    assert session.command("issues.repairs")[-1]["state"] == "DONE"
    assert published == ["recovered"] and not records(session, provider="tasks.v1")
