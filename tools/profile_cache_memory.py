"""Expanded settled-state inventory; profiler's ordinary 4096-handle cap stays unchanged."""

from collections import Counter, defaultdict
from types import SimpleNamespace

from anthroforge.native import memory
from anthroforge.native.fiber_deformation import Preparation as FiberPreparation
from anthroforge.native.paths import Path
from anthroforge.profiling import construction_inventory as construction
from anthroforge.profiling import resource_inventory as resources
from anthroforge.profiling.resources import retain_cache

LIMIT = 65536


def owners(session, observer):
    result = defaultdict(set)
    for name, documents in resources.document_owners(session).items():
        for document in documents:
            result[name].update(resources.document_resources(session, document, observer))
    result["catalogue"].update(resources.catalogue_resources(session))
    for cache in session.engine.caches():
        retain_cache(result["cache"], cache)
    for value in tuple(result["cache"]):
        if isinstance(value, FiberPreparation):
            result["cache"].update((value.field, value.field.path, *value.meshes))
    result["noncache_union"] = set().union(*(v for k, v in result.items() if k != "cache"))
    return result


def mesh_inventory(engine, groups):
    found, total = memory.snapshot(engine, LIMIT)
    assert len(found) == total, "Expanded mesh inventory is incomplete"
    rows = [[engine.library._handle, *r] for r in found]
    handles = {(r[0], r[1]): r[2] for r in rows}
    sizes = {r[2]: sum(r[3:6]) for r in rows}
    return resources.memory_totals(rows, sizes, resources.owner_groups(groups, handles), total)


def path_inventory(engine, groups):
    rows, total = memory.path_snapshot(engine, LIMIT)
    assert len(rows) == total, "Expanded path inventory is incomplete"
    sizes = {r[0]: r[2] for r in rows}
    handles = {k: {v.handle for v in values if isinstance(v, Path)} for k, values in groups.items()}
    return resources.memory_totals(rows, sizes, handles, total)


def detailed(session):
    observer = SimpleNamespace(native=SimpleNamespace(engines=[session.engine]), losses=Counter())
    groups = owners(session, observer)
    other = construction.inventories(observer, groups)
    other["paths"] = path_inventory(session.engine, groups)
    report = construction.merge(mesh_inventory(session.engine, groups), other)
    report["cache_exclusive_bytes"] = (
        report["unique_bytes"]
        - report["unattributed_bytes"]
        - report["owners"]["noncache_union"]["bytes"]
    )
    report["note"] = (
        "Settled states only; fiber solver charges remain separate conservative estimates."
    )
    return report
