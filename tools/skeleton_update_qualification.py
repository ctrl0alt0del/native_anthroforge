"""Read-only 96-muscle replacement qualification and reproducible profiler evidence."""

import hashlib
import json
import sys
from contextlib import closing
from dataclasses import replace
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace
from uuid import uuid4

import assembly_qualification as fidelity
import numpy as np
import psutil

from anthroforge.application import projects, storage
from anthroforge.application.assets import Asset
from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core.construction import Curve
from anthroforge.core.entities import SCP
from anthroforge.core.tissues import TissueVCP

OUTPUT = Path("build/skeleton-update-042/production")
FRAMES = ("SCP_8:driver-frame", "SCP_9:driver-frame", "SCP_12:driver-frame")


def report(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / (name + ".json")).write_text(json.dumps(value, indent=2), "utf-8")
    print(name, json.dumps(value)[:1400], flush=True)


def snapshot(session):
    return SimpleNamespace(
        document=session.document,
        resources=session.resources.snapshot(),
        engine=session.engine,
        assets=session.assets.copy(),
    )


def compare(before, after, identities):
    frames = tuple(Frames(s.engine, s.document) for s in (before, after))
    differences = {}
    for old in before.document.registry.records.values():
        target = identities.get(old.id, old.id)
        if isinstance(old, (SCP, TissueVCP, Curve)) and target in after.document.registry.records:
            new = after.document.object(target)
            a, b = fidelity.arrays(before, old, frames[0]), fidelity.arrays(after, new, frames[1])
            delta = compare_arrays(a, b)
            if delta:
                differences[old.id] = dict(name=old.name, differences=delta)
    return differences


def compare_arrays(a, b):
    found = {}
    for key, first in a.items():
        second = b.get(key, np.empty(0))
        if first.shape != second.shape:
            found[key] = dict(before=list(first.shape), after=list(second.shape))
        elif first.size and not np.allclose(first, second, atol=1e-8, rtol=0):
            found[key] = float(np.max(np.abs(first - second)))
    return found


def prepare(session, source, matches, choices=None):
    started = perf_counter()
    session.command("skeleton_update.inspect", path=str(source))
    state = session.command("skeleton_update.status", wait=True, timeout=600)
    inspected = perf_counter() - started
    options = dict(mappings={k: dict(action="include") for k in FRAMES}, **(choices or {}))
    session.command("skeleton_update.prepare", source=state["source"], matches=matches, **options)
    state = session.command("skeleton_update.status", wait=True, timeout=1800)
    return state, dict(inspect_s=inspected, prepare_s=perf_counter() - started - inspected)


def adopt(session, state):
    assert state["ready"], state.get("error") or state.get("findings")
    candidate = session.skeleton_update.ready(state["token"])
    expected = candidate_context(session, candidate)
    started = perf_counter()
    approved = [r["key"] for r in state["findings"] if r["acknowledge"]]
    session.command("skeleton_update.apply", token=state["token"], approved=approved)
    elapsed = perf_counter() - started
    session.wait(1800)
    delta = compare(expected, session, {})
    assert not delta, delta
    return elapsed


def candidate_context(session, candidate):
    return SimpleNamespace(
        document=candidate.document,
        resources=candidate.resources,
        engine=session.engine,
        assets=candidate.resources.meshes,
    )


def reindexed(session, bone):
    item, key = session.document.entity(bone), str(uuid4())
    resources = session.resources.snapshot()
    mesh = session.assets[item.primitive.source].mesh
    count = mesh.counts[0]
    changed = session.engine.create_mesh(
        mesh.array(0)[::-1].copy(), count - 1 - mesh.array(1), mesh.array(2)
    )
    resources.meshes[key] = Asset(changed, "qualification", "", 1, False)
    return write_reindexed(session, item, key, resources)


def write_reindexed(session, item, key, resources):
    item = replace(
        item,
        primitive=replace(item.primitive, source=key),
        asset=key,
        result=replace(item.result, asset=key),
    )
    document = replace(
        session.document,
        entities=tuple(item if e.id == item.id else e for e in session.document.entities),
    )
    path = OUTPUT / "reindexed.anthroforge"
    storage.write_package(path, document, resources)
    return path


def changed_source(session, plan):
    case = next(
        c for c in plan["cases"] if c["mapping"].get("reference", {}).get("target") == "SCP_13"
    )
    fidelity.apply_edit(session, case["mapping"], {}, case["value"])
    session.wait(1800)
    path = OUTPUT / "compatible.anthroforge"
    storage.write_package(path, session.document, session.resources)
    return path


def compatible(session, source, expected, label):
    matches = {e.id: e.id for e in session.document.entities}
    state, times = prepare(session, source, matches)
    report(label + "-review", state)
    candidate = session.skeleton_update.ready(state["token"])
    differences = compare(expected, candidate_context(session, candidate), candidate.identities)
    times["apply_s"] = adopt(session, state)
    storage.write_package(
        OUTPUT / (label + "-result.anthroforge"), session.document, session.resources
    )
    report(
        label,
        dict(times, differences=differences, peak_memory=psutil.Process().memory_info()._asdict()),
    )
    return candidate.identities


def topology_case(session):
    baseline = snapshot(session)
    path = reindexed(session, "SCP_24")
    state, times = prepare(session, path, {"SCP_24": "SCP_24"})
    report("topology-required", state)
    required = {r["key"]: True for r in state["findings"] if r["key"].startswith("rebind:")}
    assert required and not state["ready"], state
    state, times = prepare(session, path, {"SCP_24": "SCP_24"}, dict(rebind=required))
    report("topology-reviewed", state)
    times["apply_s"] = adopt(session, state)
    report("topology", dict(times, differences=compare(baseline, session, {})))


def run(source, plan):
    with closing(Session("Skeleton qualification")) as destination:
        destination.command("open", path=str(source))
        destination.wait(600)
        baseline = snapshot(destination)
        destination.command("profile.start", seconds=1800, memory_mib=256)
        compatible(destination, source, baseline, "unchanged")
        projects.adopt(destination, baseline.document, baseline.resources.snapshot())
        source_trials(destination, baseline, plan)
        topology_case(destination)
        destination.command(
            "profile.stop", path=str((OUTPUT / "update.afprofile.zip").resolve()), wait=True
        )


def source_trials(destination, baseline, plan):
    with closing(Session("Source qualification")) as edited:
        projects.adopt(edited, baseline.document, baseline.resources.snapshot())
        modified = changed_source(edited, plan)
        ids = compatible(destination, modified, edited, "compatible")
        shortcut_trials(edited, destination, ids, plan)


def shortcut_trials(source, destination, identities, plan):
    for case in plan["cases"]:
        old, current = snapshot(source), snapshot(destination)
        fidelity.apply_edit(source, case["mapping"], {}, case["value"])
        fidelity.apply_edit(destination, case["mapping"], identities, case["value"])
        source.wait(1800)
        destination.wait(1800)
        report("shortcut-" + case["id"], dict(differences=compare(source, destination, identities)))
        projects.adopt(source, old.document, old.resources.snapshot())
        projects.adopt(destination, current.document, current.resources.snapshot())


def main():
    source, plan = Path(sys.argv[1]), Path(sys.argv[2])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    run(source, json.loads(plan.read_text("utf-8")))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    report("source-integrity", dict(sha256=digest, unchanged=True))


if __name__ == "__main__":
    main()
