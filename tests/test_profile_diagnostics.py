"""Reports explain necessary work, resource overlap and bounded observation failures."""

import gc
import json
import weakref
from zipfile import ZipFile

from anthroforge.native import memory, topology
from anthroforge.profiling.resource_inventory import inventory
from tests.test_construction_contracts import create, mesh


def report(session, path):
    session.command("profile.stop", path=str(path), wait=True)
    with ZipFile(path) as archive:
        return {
            name: json.loads(archive.read(name))
            for name in ("manifest.json", "summary.json", "trace.json")
        }


def edit_curve(session, entity, height):
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    session.command(
        "point.update",
        entity=entity,
        curve=curve.id,
        point=curve.points[0].id,
        position=[0, 0, height],
    )
    session.wait(5)


def test_report_explains_revision_changes_and_warm_cache_reuse(session, tmp_path):
    session.command("profile.start", memory_mib=16)
    entity = create(session, kind="BODY")
    edit_curve(session, entity, 0.2)
    data = report(session, tmp_path / "diagnostics.zip")
    summary = data["summary.json"]["diagnostics"]
    assert summary["invalidation_reasons"]["input_output_changed"] > 0
    assert summary["cache_events"]["miss:"] and summary["cache_events"]["hit:"]
    revisions = [e for e in data["trace.json"]["traceEvents"] if e["cat"] == "revision"]
    assert any("points" in c["fields"] for e in revisions for c in e["args"]["changes"])
    assert all(e["args"]["parent"] for e in revisions)
    assert data["manifest.json"]["complete"], data["manifest.json"]["losses"]


def test_native_allocation_aliases_and_owner_overlap_do_not_double_count(session, tmp_path):
    entity = create(session, kind="BODY")
    session.command("profile.start", memory_mib=16)
    before, alias, after = alias_inventories(session, entity)
    assert alias.handle != mesh(session, entity).handle
    assert after["handles"] == before["handles"] + 1
    assert after["unique_bytes"] == before["unique_bytes"]
    attributed = after["unique_bytes"] - after["unattributed_bytes"]
    assert sum(v["bytes"] for v in after["owners"].values()) > attributed
    assert after["owners"]["document"]["bytes"] > 0
    report(session, tmp_path / "memory.zip")


def alias_inventories(session, entity):
    # Registry totals span all tests; unrelated cyclic disposal cannot delimit this measurement.
    gc.collect()
    enabled, resource = gc.isenabled(), session.profiler.resources
    gc.disable()
    try:
        before = inventory(session.profiler, resource.owners())
        alias = topology.finalize(mesh(session, entity), None, 0)
        return before, alias, inventory(session.profiler, resource.owners())
    finally:
        if enabled:
            gc.enable()


def test_profiler_off_does_not_query_memory_or_observe_cache(session, monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("Disabled profiler queried memory")

    monkeypatch.setattr(memory, "snapshot", unexpected)
    monkeypatch.setattr(memory, "path_snapshot", unexpected)
    entity = create(session, kind="BODY")
    edit_curve(session, entity, 0.2)
    session.profiler.resources.sample(force=True)
    assert session.engine.resource_observer is None and session.engine.bases.observer is None
    assert not session.profiler.resources.jobs and session.profiler.buffer is None


def test_cache_eviction_reports_its_actual_policy_reason(session, tmp_path):
    session.engine.bases.capacity = 1
    session.command("profile.start", memory_mib=16)
    entity = create(session, kind="BODY")
    piece = session.document.entity(entity).primitive.pieces[0]
    session.command("body.update", entity=entity, piece=piece.id, width=0.4)
    session.wait(5)
    data = report(session, tmp_path / "cache.zip")
    assert data["summary.json"]["diagnostics"]["cache_events"]["evict:entry_capacity"]
    assert session.engine.bases.observer is None and session.engine.resource_observer is None


def test_resource_observation_does_not_retain_meshes(session, tmp_path):
    create(session)
    session.command("profile.start", memory_mib=16)
    draft = topology.draft(next(iter(session.assets.values())).mesh, 0)
    resource = session.profiler.resources
    resource.remember("example", (draft,))
    reference = weakref.ref(draft)
    del draft
    gc.collect()
    assert reference() is None
    assert not resource.jobs["example"]
    report(session, tmp_path / "weak.zip")


def test_inventory_failure_is_explicit_and_recording_still_exports(session, tmp_path, monkeypatch):
    create(session)
    monkeypatch.setattr(memory, "snapshot", lambda *a: (_ for _ in ()).throw(ValueError("probe")))
    session.command("profile.start", memory_mib=16)
    data = report(session, tmp_path / "failure.zip")
    assert not data["manifest.json"]["complete"]
    assert data["manifest.json"]["losses"]["geometry_inventory_failure"] >= 1


def test_inventory_capacity_explicitly_reports_missing_allocations(session):
    create(session, kind="BODY")
    rows, total = memory.snapshot(session.engine, limit=1)
    assert len(rows) == 1 and total > len(rows)


def test_stopped_capture_ignores_late_job_resource_observations(session, tmp_path):
    entity = create(session, kind="BODY")
    session.command("profile.start", memory_mib=16)
    resource = session.profiler.resources
    report(session, tmp_path / "first.zip")
    resource.remember("finishing_worker", (mesh(session, entity),))
    assert not resource.jobs
    session.command("profile.start", memory_mib=16)
    resource.remember("current_worker", (mesh(session, entity),))
    assert "current_worker" in resource.jobs
    report(session, tmp_path / "second.zip")


def test_observed_job_limit_and_job_memory_are_explicit(session, tmp_path):
    entity = create(session, kind="BODY")
    session.command("profile.start", memory_mib=16)
    resource = session.profiler.resources
    for number in range(257):
        resource.remember(str(number), (mesh(session, entity),))
    assert len(resource.jobs) == 256
    evidence = inventory(session.profiler, resource.owners())
    assert evidence["owners"]["jobs"]["bytes"] > 0
    data = report(session, tmp_path / "bounded.zip")
    assert not data["manifest.json"]["complete"]
    assert data["manifest.json"]["losses"]["resource_job_limit"] == 1


def test_profile_counts_path_and_image_allocations_in_separate_namespaces(session, tmp_path):
    from tests.test_construction_resources import populated

    populated(session)
    session.command("profile.start", memory_mib=16)
    evidence = inventory(session.profiler, session.profiler.resources.owners())
    assert evidence["by_kind"]["paths"]["owners"]["document"]["bytes"] > 0
    assert evidence["by_kind"]["images"]["allocations"] == 1
    assert evidence["unique_bytes"] == sum(
        row["unique_bytes"] for row in evidence["by_kind"].values()
    )
    data = report(session, tmp_path / "construction-memory.zip")
    assert data["summary.json"]["diagnostics"]["geometry_memory"]["latest"]["by_kind"]["paths"]
    assert data["manifest.json"]["complete"], data["manifest.json"]["losses"]


def test_path_memory_inventory_reports_capacity_without_retaining_buffers(session):
    key = session.command("curve.create")
    session.wait(5)
    native = session.resources.paths[session.document.object(key).result.asset].path
    rows, count = memory.path_snapshot(session.engine, limit=0)
    assert not rows and count >= 1
    session.profiler.resources.remember("off", (native,))
    assert not session.profiler.resources.jobs
