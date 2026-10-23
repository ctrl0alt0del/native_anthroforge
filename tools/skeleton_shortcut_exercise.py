"""Exercise real migrated controls, accepted dependencies and undo with runtime reports."""

import json
import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from skeleton_shortcut_guides import settled

from anthroforge.application.session import Session


def geometry(session):
    return {
        e.id: (e.matrix, session.assets[e.result.asset or e.asset].mesh.array(0).copy())
        for e in session.document.entities
        if e.result.asset or e.asset
    }


def delta(session, before):
    current = geometry(session)
    return {
        key: dict(
            matrix=float(np.max(np.abs(np.asarray(old[0]) - current[key][0]))),
            vertices=float(np.max(np.abs(old[1] - current[key][1]))),
        )
        for key, old in before.items()
    }


def edit(session, mapping):
    value = mapping["value"]
    value = value * 1.05 if value else 0.05
    if "driver" in mapping:
        session.command("driver.value", driver=mapping["driver"], value=value)
    else:
        session.command("shortcut.set", reference=mapping["reference"], value=value)
    return value


def exercise(session, folder, mappings, number):
    key = "SHORTCUT_" + str(number)
    before, started = geometry(session), perf_counter()
    session.command("profile.start")
    value = edit(session, mappings[key])
    submitted = perf_counter() - started
    settled(session)
    elapsed, changes = perf_counter() - started, delta(session, before)
    session.command("profile.stop", path=str(folder / f"edit-{number}.afprofile.zip"), wait=True)
    record_edit(folder, number, key, value, submitted, elapsed, changes, session.scheduler.errors)
    session.command("save", path=str(folder / f"edit-{number}.anthroforge"), blocked_policy="wait")
    restore(session, before)


def record_edit(folder, number, key, value, submitted, elapsed, changes, errors):
    record = dict(
        shortcut=key,
        value=value,
        submit_seconds=submitted,
        settle_seconds=elapsed,
        changes=changes,
        errors=errors,
    )
    (folder / f"edit-{number}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record), flush=True)


def restore(session, before):
    session.command("undo")
    settled(session)
    differences = delta(session, before)
    assert max(max(row.values()) for row in differences.values()) < 1e-8, differences
    assert not session.scheduler.errors, session.scheduler.errors


def run(folder, numbers, compact=False):
    mapping = "compact-mapping.json" if compact else "complete-mapping.json"
    project = "compact-checkpoint.anthroforge" if compact else "pelvic-checkpoint.anthroforge"
    destination = folder / "compact-edits" if compact else folder
    destination.mkdir(exist_ok=True)
    mappings = json.loads((folder / mapping).read_text(encoding="utf-8"))
    with closing(Session()) as session:
        session.command("open", path=str(folder / project))
        settled(session)
        for number in numbers:
            exercise(session, destination, mappings, number)


if __name__ == "__main__":
    run(
        Path(sys.argv[1]),
        [int(v) for v in sys.argv[2:] if v != "--compact"],
        "--compact" in sys.argv,
    )
