"""Immutable preparation can be shared; its cache cannot retain unbounded tissue history."""

import weakref
from dataclasses import replace

from anthroforge.application.tissue_stack_scene import lease
from tests.test_profile_diagnostics import report
from tests.test_tissue_workflow import assembly


def prepared(session):
    _, _, key = assembly(session)
    state = session.document.object(key).intrinsic_material
    session.engine.tissue_materials.clear()
    return state, lease(session.resources, state, "a", 0)


def test_material_cache_reuses_complete_input_and_eviction_keeps_live_lease(session):
    state, value = prepared(session)
    assert lease(session.resources, state, "a", 0) is value
    cache, old = session.engine.tissue_materials, weakref.ref(value)
    cache.capacity = 1
    changed = replace(state, reverse=not state.reverse)
    second = lease(session.resources, changed, "a", 0)
    assert second is not value and value.domain(1).vertices > 0
    assert cache.bytes <= cache.budget and len(cache.retained()) == 1
    del value
    assert old() is None
    cache.clear()
    assert cache.bytes == 0 and second.domain(2).vertices > 0


def test_oversize_preparation_bypasses_storage(session):
    state, _ = prepared(session)
    session.engine.tissue_materials.clear()
    session.engine.tissue_materials.budget = 1
    value = lease(session.resources, state, "a", 0)
    assert value.retained_bytes > value.bytes > 1
    assert not session.engine.tissue_materials.retained()


def test_profiler_attributes_material_cache_and_releases_observation(session, tmp_path):
    state, value = prepared(session)
    session.command("profile.start", memory_mib=16)
    assert lease(session.resources, state, "a", 0) is value
    data = report(session, tmp_path / "materials.afprofile.zip")
    memory = data["summary.json"]["diagnostics"]["geometry_memory"]["latest"]
    assert memory["by_kind"]["tissue_materials"]["unique_bytes"] == value.bytes
    assert memory["by_kind"]["tissue_materials"]["owners"]["cache"]["allocations"] == 1
    events = data["trace.json"]["traceEvents"]
    assert any(e["cat"] == "cache" and e["args"].get("cache") == "tissue_material" for e in events)
    assert session.engine.tissue_materials.observer is None
