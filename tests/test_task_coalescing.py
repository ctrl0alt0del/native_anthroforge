"""Pending computation contracts renew without manufacturing obsolete jobs."""

from dataclasses import replace

from anthroforge.application import dependencies
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.results import Port
from tests.test_task_coordination import attachment_job
from tests.test_task_coordination import coordinated as coordinated


def renewable(published, document):
    job = attachment_job(published, 500)
    dependencies.renewable_contract(job, document, {Port("child", "pose")})
    return job


def test_repeated_uncaptured_requests_share_identity_deadline_and_fresh_dispatch(coordinated):
    coordinator, now, state, published = coordinated
    job = renewable(published, state[0])
    coordinator.submit(job)
    deadline = job.ready_at
    for revision in range(1, 20):
        state[0] = replace(state[0], revision=revision)
        coordinator.invalidate_ports({Port("child", "pose")})
        assert coordinator.submit(renewable(published, state[0])) == job.id
    assert len(coordinator.jobs) == 1 and job.ready_at == deadline
    now[0] = deadline
    coordinator.wait(2)
    assert len(published) == 1 and published[0][0] == 19


def hierarchy():
    return (
        SCP("Root", id="root"),
        SCP("Other", id="other", parent="root"),
        SCP("Child", id="child", parent="root"),
    )


def test_changed_relationship_renews_wait_and_invalidation_indexes(coordinated):
    coordinator, _, state, published = coordinated
    root, other, child = hierarchy()
    state[0] = Document(entities=(root, other, child))
    job = renewable(published, state[0])
    coordinator.submit(job)
    state[0] = replace(state[0], entities=(root, other, replace(child, parent="other")))
    coordinator.invalidate({"child"})
    assert job.state == "queued" and coordinator._refresh_pending(job)
    assert Port("other", "pose") in job.prerequisites
    assert job in coordinator.registry.matching("port", {Port("other", "pose")})
    assert coordinator.registry.matching("output", {"child"}) == [job]


def test_explicit_cancel_and_undo_remain_real_cancellation(coordinated):
    coordinator, _, state, published = coordinated
    job = renewable(published, state[0])
    coordinator.submit(job)
    coordinator.cancel_job(job.id)
    assert job.state == "cancelled"
    next_job = renewable(published, state[0])
    assert coordinator.submit(next_job) != job.id
    coordinator.restore({9})
    assert next_job.state == "obsolete" and not coordinator.active_jobs


def test_changed_output_reservation_is_not_merged(coordinated):
    coordinator, _, state, published = coordinated
    first = renewable(published, state[0])
    coordinator.submit(first)
    next_job = renewable(published, state[0])
    next_job.outputs = frozenset(("child", "other"))
    assert coordinator.submit(next_job) != first.id
    assert first.state == "obsolete" and next_job.outputs == {"child", "other"}
