"""Explicit one-project counterpart migration; no name-based general import policy."""

import json
from collections import Counter
from contextlib import closing
from dataclasses import asdict, replace
from pathlib import Path

from anthroforge.application import (
    attachment_assets,
    mirror_attachment_checks,
    mirror_bindings,
    projects,
    storage,
    surface_providers,
)
from anthroforge.application.inspection_context import freeze
from anthroforge.application.session import Session
from anthroforge.core import graph_records
from anthroforge.core.mirroring import MirrorRule, SharedMirrorTarget
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import comparison, measurement, point_attachments
from anthroforge.native.construction import matrix

SOURCE = Path("E:/development/WIP_models/shortcut_migration_030_20261023")
SOURCE /= "skeleton_96_muscles_shortcuts_v001.anthroforge"
OUTPUT = Path("build/assembly-live-mirroring")
RULE = "SCP_1"


def report(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / (name + ".json")).write_text(json.dumps(value, indent=2), "utf-8")
    print(name, json.dumps(value)[:1800], flush=True)


def opposite(key):
    return key.endswith("_mirror") or key.endswith(":mirror") or "_mirror:" in key


def removed(document):
    return {key for key in document.registry.records if opposite(key)}


def crossing_references(document, keys):
    result = []
    records = reference_records(document)
    for item in records:
        if getattr(item, "id", "") not in keys:
            result.extend(
                dict(owner=getattr(item, "id", ""), **asdict(ref))
                for ref in graph_records.references(item)
                if ref.target in keys
            )
    return result


def reference_records(document):
    return (*document.registry.records.values(), *document.shortcuts, *document.driving_shortcuts)


def retained(document):
    keys = removed(document)
    assert not crossing_references(document, keys), crossing_references(document, keys)
    fields = {
        name: tuple(v for v in getattr(document, name) if v.id not in keys)
        for name in ("entities", "objects", "controls")
    }
    return replace(document, **fields)


def candidate(document):
    original = document
    document = retained(document)
    bilateral = {e.id.removesuffix("_mirror") for e in original.entities if opposite(e.id)}
    bilateral |= {v.id for v in document.objects if isinstance(v, TissueVCP)}
    bilateral.add("SCP_7")
    rule = MirrorRule(RULE, enabled=True, axis="Y", scope=tuple(sorted(bilateral)))
    midline = {e.id for e in document.entities} - bilateral - {RULE}
    rules = (rule, *(MirrorRule(key, inherit=False) for key in sorted(midline)))
    document = replace(document, mirror_rules=rules)
    return replace(document, shared_mirror_targets=shared_targets(document))


def shared_targets(document):
    shared = {
        SharedMirrorTarget(v.source, key)
        for v in document.mirrors.instances.values()
        for key, ref in mirror_bindings.references(document.object(v.source))
        if f"mirror/{RULE}/{ref.target}" not in document.mirrors.instances
    }
    return tuple(sorted(shared, key=repr))


def inspect(session, document):
    instances = document.mirrors.instances.values()
    instance_summary(document)
    projects.adopt(session, document, session.resources)
    rows = [
        row for v in instances for row in session.command("mirror.attachment.inspect", target=v.id)
    ]
    report("relationships", rows)
    report("relationship-summary", dict(Counter(r["status"] for r in rows)))
    probe_midline(session, [r for r in rows if r["status"] == "mismatch"])


def instance_summary(document):
    instances = document.mirrors.instances.values()
    report(
        "instances",
        dict(
            count=len(document.mirrors.instances),
            kinds=dict(Counter(type(document.object(v.source)).__name__ for v in instances)),
            conflicts=document.mirrors.conflicts,
            shared=len(document.shared_mirror_targets),
        ),
    )


def probe_frames(context, row):
    item = context.document.object(row["source"])
    ref = SurfaceReference(**row["reference"])
    source = mirror_attachment_checks.resolved_frame(context, item, row["binding"], ref)
    plane = context.document.mirrors.rules[RULE].frame
    return source[3:12:4], matrix(context.engine, plane, source)[3:12:4]


def probe_midline(session, rows):
    context = freeze(session)
    targets = tuple(dict.fromkeys(SurfaceReference(**r["reference"]) for r in rows))
    bindings = probe_captures(context, rows, targets)
    distances = [measurement.distance(session.engine, (0, 0, 0), b[15:18])[3] for b in bindings]
    result = [gap_row(row, distances[i * 2 : i * 2 + 2]) for i, row in enumerate(rows)]
    report("midline-surface-gaps", result)
    summary = {
        ref.target: max(r["reflected_gap"] for r in result if r["target"] == ref.target)
        for ref in targets
    }
    report("midline-gap-summary", summary)


def probe_captures(context, rows, targets):
    inputs = attachment_assets.surface_inputs(
        context.engine, context.document, context.assets, targets
    )
    positions = [p for row in rows for p in probe_frames(context, row)]
    forced = [targets.index(SurfaceReference(**row["reference"])) for row in rows for _ in range(2)]
    return point_attachments.capture(context.engine, *inputs, positions, forced)[1]


def gap_row(row, distances):
    return dict(
        source=row["source"],
        binding=row["binding"],
        target=row["reference"]["target"],
        original_gap=distances[0],
        reflected_gap=distances[1],
    )


def main():
    with closing(Session()) as session:
        document, resources = storage.read_package(SOURCE, session.engine)
        projects.adopt(session, document, resources)
        keys = removed(document)
        report("removed", sorted(keys))
        report("crossing-references", crossing_references(document, keys))
        migrated = candidate(document)
        compare_bones(session, document, migrated)
        inspect(session, migrated)
        storage.atomic_save(OUTPUT / "candidate.anthroforge", migrated, resources)


def compare_bones(session, original, migrated):
    pairs = [
        bone_pair(session, original, migrated, item)
        for item in original.entities
        if opposite(item.id)
    ]
    report("bone-shape-comparison", pairs)


def bone_pair(session, original, migrated, item):
    source = item.id.removesuffix("_mirror")
    old = surface_providers.get(session.engine, original, session.assets, item.id)
    new = surface_providers.get(
        session.engine, migrated, session.assets, SurfaceReference(source, instance=RULE)
    )
    delta = comparison.distances(old.resource.mesh, old.frame, new.resource.mesh, new.frame, False)
    return dict(original=item.id, source=source, **delta)


if __name__ == "__main__":
    main()
