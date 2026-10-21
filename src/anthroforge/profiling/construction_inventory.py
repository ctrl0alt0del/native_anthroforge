"""Typed path/image inventories keep native handle namespaces distinct from mesh handles."""

from anthroforge.application.image_assets import ImageAsset
from anthroforge.native import memory
from anthroforge.native.attachment_fields import Field
from anthroforge.native.binding_batches import BindingBatch
from anthroforge.native.inspection import Comparison
from anthroforge.native.paths import Path
from anthroforge.native.routing_scene import RoutingScene
from anthroforge.native.strokes import Stroke
from anthroforge.native.tissue_stacking import MaterialLease


def inventories(profiler, owners):
    return dict(
        paths=path_inventory(profiler, owners),
        images=image_inventory(owners),
        strokes=stroke_inventory(owners),
        attachments=attachment_inventory(owners),
        routing_scenes=routing_scene_inventory(owners),
        tissue_materials=tissue_material_inventory(owners),
        tissue_comparisons=comparison_inventory(owners),
    )


def comparison_inventory(owners):
    from .resource_inventory import memory_totals

    values = {v for group in owners.values() for v in group if isinstance(v, Comparison)}
    sizes = {id(v): v.bytes for v in values}
    groups = {
        name: {id(v) for v in group if isinstance(v, Comparison)} for name, group in owners.items()
    }
    return memory_totals(list(values), sizes, groups, len(values))


def tissue_material_inventory(owners):
    from .resource_inventory import memory_totals

    values = {v for group in owners.values() for v in group if isinstance(v, MaterialLease)}
    sizes = {id(v): v.bytes for v in values}
    groups = {
        name: {id(v) for v in group if isinstance(v, MaterialLease)}
        for name, group in owners.items()
    }
    return memory_totals(list(values), sizes, groups, len(values))


def routing_scene_inventory(owners):
    from .resource_inventory import memory_totals

    scenes = {v for values in owners.values() for v in values if isinstance(v, RoutingScene)}
    sizes = {id(v): v.bytes for v in scenes}
    groups = {
        name: {id(v) for v in values if isinstance(v, RoutingScene)}
        for name, values in owners.items()
    }
    return memory_totals(list(scenes), sizes, groups, len(scenes))


def attachment_inventory(owners):
    from .resource_inventory import memory_totals

    fields = {
        v for values in owners.values() for v in values if isinstance(v, (Field, BindingBatch))
    }
    sizes = {id(v): v.bytes for v in fields}
    groups = {
        name: {id(v) for v in values if isinstance(v, (Field, BindingBatch))}
        for name, values in owners.items()
    }
    return memory_totals(list(fields), sizes, groups, len(fields))


def path_inventory(profiler, owners):
    from .resource_inventory import memory_totals

    rows, total = path_rows(profiler)
    sizes = {(row[0], row[1]): row[3] for row in rows}
    groups = {
        name: {(v.engine.library._handle, v.handle) for v in values if isinstance(v, Path)}
        for name, values in owners.items()
    }
    groups = {name: keys & sizes.keys() for name, keys in groups.items()}
    return memory_totals(rows, sizes, groups, total)


def stroke_inventory(owners):
    from .resource_inventory import memory_totals

    strokes = {v for values in owners.values() for v in values if isinstance(v, Stroke)}
    sizes = {id(v): v.bytes for v in strokes}
    groups = {
        name: {id(v) for v in values if isinstance(v, Stroke)} for name, values in owners.items()
    }
    return memory_totals(list(strokes), sizes, groups, len(strokes))


def image_inventory(owners):
    from .resource_inventory import memory_totals

    images = {v for values in owners.values() for v in values if isinstance(v, ImageAsset)}
    sizes = {id(v): image_bytes(v) for v in images}
    groups = {
        name: {id(v) for v in values if isinstance(v, ImageAsset)}
        for name, values in owners.items()
    }
    return memory_totals(list(images), sizes, groups, len(images))


def image_bytes(image):
    return len(image.encoded) + len(image.rgba) + (image.texture.bytes if image.texture else 0)


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
