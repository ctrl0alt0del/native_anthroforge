"""Typed path/image inventories keep native handle namespaces distinct from mesh handles."""

from anthroforge.application.image_assets import ImageAsset
from anthroforge.native import memory
from anthroforge.native.paths import Path


def inventories(profiler, owners):
    from .resource_inventory import memory_totals

    rows, total = path_rows(profiler)
    sizes = {(row[0], row[1]): row[3] for row in rows}
    groups = {
        name: {(v.engine.library._handle, v.handle) for v in values if isinstance(v, Path)}
        for name, values in owners.items()
    }
    groups = {name: keys & sizes.keys() for name, keys in groups.items()}
    return dict(paths=memory_totals(rows, sizes, groups, total), images=image_inventory(owners))


def image_inventory(owners):
    from .resource_inventory import memory_totals

    images = {v for values in owners.values() for v in values if isinstance(v, ImageAsset)}
    sizes = {id(v): len(v.encoded) + len(v.rgba) for v in images}
    groups = {
        name: {id(v) for v in values if isinstance(v, ImageAsset)}
        for name, values in owners.items()
    }
    return memory_totals(list(images), sizes, groups, len(images))


def path_rows(profiler):
    libraries, rows, total = set(), [], 0
    for engine in profiler.native.engines:
        if engine.library._handle in libraries:
            continue
        libraries.add(engine.library._handle)
        found, count = memory.path_snapshot(engine, max(0, 4096 - len(rows)))
        rows.extend([engine.library._handle, *row] for row in found)
        total += count
        if len(found) != count:
            profiler.losses["resource_path_inventory_limit"] += 1
    return rows, total


def merge(meshes, construction):
    kinds = dict(meshes=meshes, **construction)
    totals = {
        key: sum(row[key] for row in kinds.values())
        for key in ("unique_bytes", "allocations", "handles", "total_handles", "unattributed_bytes")
    }
    return dict(
        totals,
        owners=merged_owners(kinds),
        by_kind=kinds,
        limits=meshes["limits"],
        complete=all(row["complete"] for row in kinds.values()),
    )


def merged_owners(kinds):
    names = set().union(*(row["owners"].keys() for row in kinds.values()))
    return {
        name: {
            key: sum(row["owners"].get(name, {}).get(key, 0) for row in kinds.values())
            for key in ("bytes", "allocations")
        }
        for name in names
    }
