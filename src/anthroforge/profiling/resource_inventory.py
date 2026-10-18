"""Allocation deduplication and overlapping ownership; geometry arrays never enter traces."""

from dataclasses import fields, is_dataclass
from itertools import islice

from anthroforge.native import memory
from anthroforge.native.mesh import Mesh

LIMITATIONS = [
    "Native mesh payload capacity, including estimated full-binary AABB node bytes",
    "Excludes allocator overhead, Python objects, Qt copies and GPU/driver allocations",
    "Ownership totals overlap; add neither owners nor shared alias handles",
    "Pre-recording job payload references may be unattributed; job snapshots are included",
    "Snapshots are event-driven at most once per second, plus recording boundaries",
]


def payload_meshes(value, profiler):
    pending, found, seen = [value], set(), set()
    for _ in range(8192):
        if not pending:
            break
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, Mesh):
            found.add(item)
        else:
            pending.extend(bounded(children(item), 8192 - len(seen) - len(pending), profiler))
    return finish_payload(found, pending, profiler)


def finish_payload(found, pending, profiler):
    if pending:
        profiler.losses["resource_payload_limit"] += 1
    return found


def children(value):
    if isinstance(value, dict):
        return value.values()
    if isinstance(value, (list, tuple)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return (
            getattr(value, field.name)
            for field in fields(value)
            if field.name in ("mesh", "assets")
        )
    return ()


def session_owners(session, output, profiler):
    documents = dict(
        document=[session.document],
        checkpoint=[session.scheduler.checkpoint],
        history=(entry.document for entry in session.history.entries),
    )
    documents["jobs"] = [job.snapshot for job in session.scheduler.active_jobs if job.snapshot]
    documents["edit"] = [session.history.before] if session.history.before else []
    for owner, values in documents.items():
        keys = document_assets(bounded(values, 512, profiler), profiler)
        output[owner].update(session.assets[key].mesh for key in keys if key in session.assets)
    output["catalogue"].update(a.mesh for a in bounded(session.assets.values(), 4096, profiler))


def bounded(values, limit, profiler):
    iterator = iter(values)
    result = list(islice(iterator, max(0, limit)))
    if next(iterator, None) is not None:
        profiler.losses["resource_inventory_truncated"] += 1
    return result


def document_assets(documents, profiler):
    from anthroforge.core.results import geometry_asset

    keys = set()
    for document in documents:
        for item in bounded(document.entities, 4096, profiler):
            keys.add(geometry_asset(item))
            if item.primitive:
                keys.add(item.primitive.source)
        if len(keys) > 4096:
            return set(bounded(keys, 4096, profiler))
    return keys - {""}


def inventory(profiler, owners):
    rows, total = native_rows(profiler)
    handles = {(row[0], row[1]): row[2] for row in rows}
    allocations = {row[2]: row for row in rows}
    sizes = {identity: sum(row[3:6]) for identity, row in allocations.items()}
    groups = owner_groups(owners, handles)
    report = memory_totals(rows, sizes, groups, total)
    report["complete"] &= not any(k.startswith("resource_") for k in profiler.losses)
    return report


def memory_totals(rows, sizes, groups, total):
    attributed = set().union(*groups.values())
    return dict(
        unique_bytes=sum(sizes.values()),
        allocations=len(sizes),
        handles=len(rows),
        total_handles=total,
        complete=len(rows) == total,
        owners=owner_totals(sizes, groups),
        unattributed_bytes=sum(size for key, size in sizes.items() if key not in attributed),
        limits=LIMITATIONS,
    )


def owner_totals(sizes, groups):
    return {
        name: dict(bytes=sum(sizes[key] for key in ids), allocations=len(ids))
        for name, ids in groups.items()
    }


def owner_groups(owners, handles):
    groups = {}
    for name, meshes in owners.items():
        keys = ((mesh.engine.library._handle, mesh.handle) for mesh in meshes)
        groups[name] = {handles[key] for key in keys if key in handles}
    return groups


def native_rows(profiler):
    libraries, rows, total = set(), [], 0
    for engine in profiler.native.engines:
        if engine.library._handle in libraries:
            continue
        libraries.add(engine.library._handle)
        found, count = memory.snapshot(engine, max(0, 4096 - len(rows)))
        rows.extend([engine.library._handle, *row] for row in found)
        total += count
        if len(found) != count:
            profiler.losses["geometry_inventory_limit"] += 1
    return rows, total
