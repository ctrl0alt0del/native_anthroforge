"""Allocation deduplication and overlapping ownership; geometry arrays never enter traces."""

from dataclasses import fields, is_dataclass
from itertools import islice

from anthroforge.application.image_assets import ImageAsset
from anthroforge.application.resources import Resources as ResourceCatalogue
from anthroforge.application.skin_assets import SkinAsset
from anthroforge.native import memory
from anthroforge.native.attachment_fields import Field
from anthroforge.native.binding_batches import BindingBatch
from anthroforge.native.inspection import Comparison
from anthroforge.native.mesh import Mesh
from anthroforge.native.path_collisions import CollisionCache
from anthroforge.native.paths import Path
from anthroforge.native.routing_scene import RoutingScene
from anthroforge.native.stacking import StackSession
from anthroforge.native.tissue_preparation import Preparation
from anthroforge.native.tissue_stacking import MaterialLease

LIMITATIONS = [
    "Native mesh/path payload capacities; meshes include estimated full-binary AABB node bytes",
    "Images include owned encoded source and decoded RGBA bytes reachable from observed owners",
    "Routing scene capacities include observed cache/job captures; allocator overhead excluded",
    "Tissue preparation includes owned arrays/visible meshes; source meshes counted separately",
    "Excludes allocator overhead, Python objects, Qt copies and GPU/driver allocations",
    "Ownership totals overlap; add neither owners nor shared alias handles",
    "Stacking session storage is a conservative bound including opaque vector-cache allowance",
    "Pre-recording job payload references may be unattributed; job snapshots are included",
    "Snapshots are event-driven at most once per second, plus recording boundaries",
]
RESOURCE_FIELDS = frozenset(
    (
        "mesh",
        "asset",
        "assets",
        "path",
        "paths",
        "meshes",
        "images",
        "resources",
        "field",
        "attachment",
        "attachments",
        "bindings",
        "context",
        "source",
        "baseline",
        "comparison",
        "skin",
    )
)
RESOURCE_TYPES = (
    Mesh,
    Path,
    ImageAsset,
    Field,
    RoutingScene,
    BindingBatch,
    MaterialLease,
    Comparison,
    CollisionCache,
    StackSession,
    Preparation,
    SkinAsset,
)


def payload_resources(value, profiler, group=None):
    pending, found, seen = [value], set(), set()
    for _ in range(8192):
        if not pending:
            break
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        remaining = 8192 - len(seen) - len(pending)
        pending.extend(bounded(observe_item(item, found, group), remaining, profiler))
    return finish_payload(found, pending, profiler)


def observe_item(item, found, group):
    if isinstance(item, ResourceCatalogue) and group is not None:
        group(item)
    elif isinstance(item, RESOURCE_TYPES):
        found.update(native_resources(item))
    else:
        return children(item)
    return ()


def native_resources(item):
    return (
        item,
        *((item.path,) if isinstance(item, Field) else ()),
        *getattr(item, "resources", ()),
    )


def finish_payload(found, pending, profiler):
    if pending:
        profiler.losses["resource_payload_limit"] += 1
    return found


def children(value):
    if isinstance(value, ResourceCatalogue):
        return owned_resources(value)
    if isinstance(value, dict):
        return value.values()
    if isinstance(value, (list, tuple)):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return (
            getattr(value, field.name) for field in fields(value) if field.name in RESOURCE_FIELDS
        )
    return ()


def document_owners(session):
    documents = dict(
        document=[session.document],
        checkpoint=[session.scheduler.checkpoint],
        history=(entry.document for entry in session.history.entries),
    )
    documents["jobs"] = [job.snapshot for job in session.scheduler.active_jobs if job.snapshot]
    documents["edit"] = [session.history.before] if session.history.before else []
    return documents


def session_owners(session, output, profiler):
    for owner, values in document_owners(session).items():
        references = (
            resource
            for document in bounded(values, 512, profiler)
            for resource in document_resources(session, document, profiler)
        )
        output[owner].update(bounded_unique(references, 4096, profiler))
    output["catalogue"].update(bounded(catalogue_resources(session), 4096, profiler))
    preview_owners(session, output)
    replacement_owners(session, output)
    inspection_owners(session, output, profiler)
    comparison_owners(session, output)


def comparison_owners(session, output):
    baseline = session.shortcut_comparison.baseline
    if baseline:
        output["comparison_baseline"].update(owned_resources(baseline.source.resources))


def preview_owners(session, output):
    for name, attribute in (
        ("conversion", "path"),
        ("surface_preview", "mesh"),
        ("tissue_preview", "mesh"),
    ):
        preview = getattr(session, name)
        if preview.asset is not None:
            output["conversion_preview" if name == "conversion" else name].add(
                getattr(preview.asset, attribute)
            )


def replacement_owners(session, output):
    for name in ("mesh_replacement", "tissue_retarget"):
        candidate = getattr(session, name).asset
        if candidate:
            output["replacement_preview"].update(owned_resources(candidate.resources))


def inspection_owners(session, output, profiler):
    for value in session.tissue_inspection.values.values():
        if value.asset:
            output["tissue_inspection"].update(payload_resources(value.asset, profiler))


def catalogue_resources(session):
    return owned_resources(session.resources)


def owned_resources(resources):
    yield from (a.mesh for a in resources.meshes.values())
    yield from (a.path for a in resources.paths.values())
    yield from resources.images.values()
    yield from (a.field for a in resources.attachments.values())
    yield from (a.field.path for a in resources.attachments.values())
    yield from resources.bindings.values()
    yield from resources.skin.values()


def bounded_unique(values, limit, profiler):
    found = set()
    for value in values:
        if value in found:
            continue
        if len(found) >= limit:
            profiler.losses["resource_inventory_truncated"] += 1
            break
        found.add(value)
    return found


def bounded(values, limit, profiler):
    iterator = iter(values)
    result = list(islice(iterator, max(0, limit)))
    if next(iterator, None) is not None:
        profiler.losses["resource_inventory_truncated"] += 1
    return result


def document_resources(session, document, profiler):
    from anthroforge.application.resources import references

    keys = references(
        bounded(document.entities, 4096, profiler), bounded(document.objects, 4096, profiler)
    )
    resources = session.resources
    meshes, paths, images = resources.meshes, resources.paths, resources.images
    result = [meshes[key].mesh for key in keys["meshes"] if key in meshes]
    result.extend(paths[key].path for key in keys["paths"] if key in paths)
    result.extend(images[key] for key in keys["images"] if key in images)
    result.extend(attachment_resources(session, keys["attachments"]))
    result.extend(resources.bindings[k] for k in keys["bindings"] if k in resources.bindings)
    return result + skin_resources(resources, document.skin)


def skin_resources(resources, skin):
    from anthroforge.application.skin_assets import references

    meshes, arrays = references(skin)
    return [resources.meshes[k].mesh for k in meshes if k in resources.meshes] + [
        resources.skin[k] for k in arrays if k in resources.skin
    ]


def attachment_resources(session, keys):
    for key in keys:
        if key in session.resources.attachments:
            field = session.resources.attachments[key].field
            yield field
            yield field.path


def inventory(profiler, owners):
    from .construction_inventory import inventories, merge

    rows, total = native_rows(profiler)
    handles = {(row[0], row[1]): row[2] for row in rows}
    allocations = {row[2]: row for row in rows}
    sizes = {identity: sum(row[3:6]) for identity, row in allocations.items()}
    groups = owner_groups(owners, handles)
    report = merge(memory_totals(rows, sizes, groups, total), inventories(profiler, owners))
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
        keys = (
            (mesh.engine.library._handle, mesh.handle) for mesh in meshes if isinstance(mesh, Mesh)
        )
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
