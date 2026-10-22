"""Catalogue observation is bounded, weak, and does not repeatedly enumerate jobs."""

import gc
import weakref
from unittest.mock import patch

from anthroforge.profiling.resource_inventory import bounded_unique
from tests.test_construction_contracts import create, mesh
from tests.test_profile_diagnostics import report


def test_payload_catalogues_are_observed_without_enumeration(session, tmp_path):
    entity = create(session, kind="BODY")
    session.command("profile.start", memory_mib=16)
    capture = session.resources.snapshot()
    observer = session.profiler.resources
    with patch("anthroforge.profiling.resource_inventory.children", side_effect=AssertionError):
        observer.observe_payload("job", capture)
    assert mesh(session, entity) in observer.owners()["jobs"]
    reference = weakref.ref(capture)
    del capture
    gc.collect()
    assert reference() is None
    assert mesh(session, entity) not in observer.owners()["jobs"]
    report(session, tmp_path / "groups.zip")


def test_overlapping_owner_references_do_not_exhaust_inventory_limit(session):
    entity = create(session, kind="BODY")
    resource = mesh(session, entity)
    values = bounded_unique([resource] * 10000, 1, session.profiler)
    assert values == {resource}
    assert not session.profiler.losses["resource_inventory_truncated"]


def test_group_observation_clears_at_job_and_recording_boundaries(session, tmp_path):
    create(session, kind="BODY")
    session.command("profile.start", memory_mib=16)
    capture, observer = session.resources.snapshot(), session.profiler.resources
    observer.observe_payload("job", capture)
    observer.release("job")
    assert not observer.groups.jobs
    observer.observe_payload("job", capture)
    report(session, tmp_path / "clear.zip")
    assert not observer.groups.jobs
    observer.observe_payload("late", capture)
    assert not observer.groups.jobs
