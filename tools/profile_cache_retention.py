"""Read-only-source production trials for R09/R10; no evaluator changes."""

import json
import sys
from contextlib import closing
from pathlib import Path

import numpy as np
import psutil
from profile_cache_memory import detailed
from profiler_system_load import system_load, system_times
from qualify_retained_attachment_edits import load
from shortcut_inspection_profile import PLAN, edit, fingerprint
from shortcut_parity_app_capture import record

from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP
from anthroforge.profiling.identity import build_identity
from anthroforge.profiling.resource_inventory import inventory


def snapshot(session):
    owners = session.profiler.resources.owners()
    owners["noncache_union"] = set().union(*(v for k, v in owners.items() if k != "cache"))
    observed = inventory(session.profiler, owners)
    return dict(
        memory=psutil.Process().memory_info()._asdict(),
        inventory=observed,
        expanded=detailed(session),
        caches=[cache_state(c) for c in session.engine.caches()],
        history_entries=len(session.history.entries),
        assets=len(session.assets),
        aggregate=session.engine.cache_budget.report()
        if hasattr(session.engine, "cache_budget")
        else {},
    )


def cache_state(cache):
    with cache.lock:
        return dict(
            name=cache.name,
            bytes=cache.bytes,
            entries=len(cache.items),
            budget=cache.budget,
            capacity=cache.capacity,
        )


def write(output, name, value):
    (output / (name + ".json")).write_text(json.dumps(value, indent=2), encoding="utf-8")


def trial(session, case, output, name):
    session.command("profile.start", seconds=120)
    before, clock = snapshot(session), system_times()
    edit(session, case)
    result = dict(case=case, load=system_load(clock), before=before, after=snapshot(session))
    result["errors"] = list(session.scheduler.errors)
    session.command("profile.stop", path=str(output / (name + ".afprofile.zip")), wait=True)
    write(output, name, result)
    print(name, result["load"]["wall_seconds"], result["errors"], flush=True)


def sequence(session, cases, output, cycles):
    for cycle in range(cycles):
        for index, original in enumerate(cases):
            case = dict(original)
            case["value"] = original["value"] if cycle % 2 == 0 else original["mapping"]["value"]
            trial(session, case, output, f"edit-{cycle:02d}-{index}")


def boundary(session, output, name, action):
    session.command("profile.start")
    before, geometry = snapshot(session), fingerprint(session)
    action()
    result = dict(
        before=before, after=snapshot(session), unchanged=fingerprint(session) == geometry
    )
    session.command("profile.stop", path=str(output / (name + ".afprofile.zip")), wait=True)
    write(output, name, result)


def navigate(session, output):
    for operation in ("undo", "redo"):
        session.command("profile.start")
        clock = system_times()
        for _ in range(4):
            session.command(operation)
            session.wait(600)
        result = dict(load=system_load(clock), after=snapshot(session))
        session.command(
            "profile.stop", path=str(output / (operation + ".afprofile.zip")), wait=True
        )
        write(output, operation, result)


def environment(output):
    output.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text())
    write(
        output,
        "environment",
        dict(build=build_identity(), source=plan["standalone"], cpu=psutil.cpu_count()),
    )
    return plan


def positions(session, output):
    arrays, frames = {}, Frames(session.engine, session.document)
    for item in session.document.registry.records.values():
        if isinstance(item, (SCP, TissueVCP, Fiber)):
            record(session, item, frames, arrays)
    np.savez_compressed(output / "positions.npz", **arrays)


def final_state(session, output):
    write(output, "final-fingerprint", fingerprint(session))
    if "--arrays" in sys.argv:
        positions(session, output)


def run(output, cycles, fiber_mib=None):
    plan = environment(output)
    with closing(Session()) as session:
        if fiber_mib is not None:
            session.engine.fiber_deformations.budget = fiber_mib * 1024**2
        load(session, Path(plan["standalone"]))
        write(output, "initial-fingerprint", fingerprint(session))
        sequence(session, plan["cases"], output, cycles)
        final_state(session, output)
        navigate(session, output)
        boundary(session, output, "clear-caches", session.engine.clear_caches)
        trial(session, plan["cases"][0], output, "cold-rebuild")
        boundary(session, output, "reopen-source", lambda: load(session, Path(plan["standalone"])))


if __name__ == "__main__":
    run(
        Path(sys.argv[1]).resolve(),
        int(sys.argv[2]) if len(sys.argv) > 2 else 4,
        int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else None,
    )
