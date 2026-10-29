"""Verify migrated live instances while preserving the source assembly byte-for-byte."""

import hashlib
import json
from contextlib import ExitStack, closing
from dataclasses import replace
from pathlib import Path
from time import perf_counter

import assembly_mirror_migration as migration
import assembly_qualification as assembly
import skeleton_update_qualification as fidelity

from anthroforge.application import projects, storage
from anthroforge.application.session import Session
from anthroforge.core.entities import SCP
from anthroforge.core.tissues import TissueVCP


def source_projection(before, after):
    found = after.document.registry.records
    document = before.document
    fields = {
        name: tuple(v for v in getattr(document, name) if v.id in found)
        for name in ("entities", "objects", "controls")
    }
    result = fidelity.snapshot(before)
    result.document = replace(document, **fields)
    return result


def compare_sources(before, after, label):
    changed = fidelity.compare(source_projection(before, after), after, {})
    migration.report(label, changed)
    assert not changed, label


def verify_instances(session):
    records = session.document.registry.records
    instances = session.document.mirrors.instances
    for instance in instances.values():
        assert instance.source in records
    assert sum(isinstance(records[v.source], TissueVCP) for v in instances.values()) == 96
    assert sum(isinstance(records[v.source], SCP) for v in instances.values()) == 27
    assert not any(migration.opposite(key) for key in records)
    assert not session.document.mirrors.conflicts


def change_ribs(session):
    driver = next(d for d in session.document.driving_shortcuts if d.label == "Ribs Top Radius")
    started = perf_counter()
    session.command("driver.value", driver=driver.id, value=3.0)
    session.wait(900)
    return perf_counter() - started


def updates(original, mirrored):
    timings = [change_ribs(s) for s in (original, mirrored)]
    migration.report("ribs-update-timing", dict(original_s=timings[0], mirrored_s=timings[1]))
    compare_sources(original, mirrored, "ribs-update-source-differences")
    verify_instances(mirrored)
    storage.atomic_save(
        migration.OUTPUT / "ribs3.anthroforge", mirrored.document, mirrored.resources
    )
    errors = [(j.kind, j.error) for j in mirrored.scheduler.registry.by_id.values() if j.error]
    migration.report("ribs-update-errors", errors)


def other_shortcuts(source, mirrored):
    plan = Path("E:/development/WIP_models/shortcut_update_parity_20261023/plan.json")
    for case in json.loads(plan.read_text("utf-8"))["cases"]:
        if case["label"] != "Ribs Top Radius":
            trial(source, mirrored, case)


def trial(source, mirrored, case):
    snapshots = [(s.document, s.resources.snapshot()) for s in (source, mirrored)]
    timings = [assembly.edit(s, case, {}) for s in (source, mirrored)]
    compare_sources(source, mirrored, case["id"] + "-source-differences")
    verify_instances(mirrored)
    migration.report(case["id"] + "-timing", dict(original_s=timings[0], mirrored_s=timings[1]))
    for session, snapshot in zip((source, mirrored), snapshots, strict=True):
        projects.adopt(session, *snapshot)


def qualify():
    source_hash = hashlib.sha256(migration.SOURCE.read_bytes()).hexdigest()
    with ExitStack() as stack:
        source, mirrored = [stack.enter_context(closing(Session())) for _ in range(2)]
        projects.adopt(source, *storage.read_package(migration.SOURCE, source.engine))
        path = migration.OUTPUT / "candidate.anthroforge"
        projects.adopt(mirrored, *storage.read_package(path, mirrored.engine))
        compare_sources(source, mirrored, "reopened-source-differences")
        verify_instances(mirrored)
        other_shortcuts(source, mirrored)
        updates(source, mirrored)
    assert hashlib.sha256(migration.SOURCE.read_bytes()).hexdigest() == source_hash
    migration.report("source-integrity", dict(sha256=source_hash, unchanged=True))


if __name__ == "__main__":
    qualify()
