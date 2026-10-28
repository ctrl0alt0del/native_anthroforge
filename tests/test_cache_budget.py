"""Aggregate ownership, cost eviction and outstanding leases are independent of geometry."""

from types import SimpleNamespace

from anthroforge.native.cache_budget import CacheBudget
from anthroforge.native.resource_cache import ResourceCache


def caches(budget):
    pool = CacheBudget(budget)
    first, second = (ResourceCache(1000, 10, name) for name in ("first", "second"))
    for cache in (first, second):
        pool.attach(cache)
    return pool, first, second


def test_shared_allocations_charged_once_across_caches_and_released_after_last_owner():
    pool, first, second = caches(1000)
    resource = SimpleNamespace(bytes=80)
    a, b = (SimpleNamespace(bytes=10, resources=(resource,)) for _ in range(2))
    first.store((1,), a, 90)
    second.store((2,), b, 90)
    assert first.bytes == second.bytes == 90
    assert pool.report()["bytes"] == 100
    first.clear()
    assert pool.report()["bytes"] == 90
    second.clear()
    assert pool.report()["bytes"] == 0


def test_cost_aware_eviction_keeps_expensive_rebuild(monkeypatch):
    now = [0.0]
    monkeypatch.setattr("anthroforge.native.resource_cache.perf_counter", lambda: now[0])
    pool, first, second = caches(100)
    first.get((1,))
    now[0] = 10
    expensive = first.store((1,), SimpleNamespace(bytes=60), 60)
    second.get((2,))
    now[0] += 0.01
    second.store((2,), SimpleNamespace(bytes=60), 60)
    assert first.get((1,)) is expensive and second.get((2,)) is None
    assert pool.report()["bytes"] == 60


def test_lease_clear_epoch_and_reweigh_preserve_external_resource():
    pool, first, _ = caches(100)
    value = first.store((1,), SimpleNamespace(bytes=60), 60)
    leased, epoch = first.take((1,))
    assert leased is value and pool.report()["bytes"] == 0
    first.clear()
    first.restore((1,), leased, 60, epoch)
    assert not first.retained()
    first.store((1,), value, 60)
    value.bytes = 110
    first.reweigh((1,), value, 110)
    assert not first.retained() and pool.report()["bytes"] == 0 and value.bytes == 110


def test_oversize_result_bypasses_retention_without_restricting_work():
    pool, first, _ = caches(50)
    value = SimpleNamespace(bytes=100)
    assert first.store((1,), value, 100) is value
    assert not first.items and pool.report()["bytes"] == 0


def test_native_alias_receipts_count_shared_mesh_once(session):
    from anthroforge.native.resource_footprint import footprint, mesh_receipt
    from anthroforge.native.surface_queries import Mode, prepare
    from tests.conftest import CUBE

    mesh = session.engine.import_mesh(CUBE, 1.0, False)
    query = prepare(mesh, None, Mode.PREVIEW)
    assert query.mesh.handle != mesh.handle
    assert mesh_receipt(query.mesh) == mesh_receipt(mesh)
    assert sum(footprint(query, query.bytes).values()) == sum(mesh_receipt(mesh).values())
