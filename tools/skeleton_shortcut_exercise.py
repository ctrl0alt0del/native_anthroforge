"""Exercise real migrated controls, accepted dependencies and undo with runtime reports."""

import json
import sys
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from skeleton_shortcut_guides import settled

from anthroforge.application.session import Session
from anthroforge.core.entities import IDENTITY
from anthroforge.core.results import geometry_asset


def geometry(session):
    result = {}
    for item in session.document.registry.records.values():
        if not hasattr(getattr(item, "result", None), "asset"):
            continue
        asset = geometry_asset(item)
        if asset in session.assets:
            points = session.assets[asset].mesh.array(0)
        elif asset in session.resources.paths:
            points = session.resources.paths[asset].path.array()[:, :3]
        else:
            continue
        result[item.id] = (getattr(item, "matrix", IDENTITY), points.copy())
    return result


def delta(session, before):
    current = geometry(session)
    return {
        key: dict(
            matrix=float(np.max(np.abs(np.asarray(old[0]) - current[key][0]))),
            vertices=point_delta(old[1], current[key][1]),
            count=abs(len(old[1]) - len(current[key][1])),
        )
        for key, old in before.items()
    }


def point_delta(before, after):
    return float(np.max(np.abs(before - after))) if before.shape == after.shape else 0.0


def edit(session, mapping):
    value = mapping["value"]
    value = [v * 1.05 for v in value] if isinstance(value, list) else changed_value(value)
    if "driver" in mapping:
        if session.document.formula_index.drivers[mapping["driver"]].dimension == "ANGLE":
            value = mapping["value"] + 0.05
        session.command("driver.value", driver=mapping["driver"], value=value)
    else:
        session.command("shortcut.set", reference=mapping["reference"], value=value)
    return value


def changed_value(value):
    return value * 1.05 if abs(value) > 0.1 else value + 0.05


def exercise(session, folder, mappings, number):
    key = "SHORTCUT_" + str(number)
    before, started, first_job = geometry(session), perf_counter(), len(session.scheduler.jobs)
    session.command("profile.start")
    value = edit(session, mappings[key])
    submitted = perf_counter() - started
    settled(session)
    require_ready(session)
    elapsed, changes = perf_counter() - started, delta(session, before)
    session.command("profile.stop", path=str(folder / f"edit-{number}.afprofile.zip"), wait=True)
    record_edit(
        folder, number, key, value, submitted, elapsed, changes, failures(session, first_job)
    )
    session.command("save", path=str(folder / f"edit-{number}.anthroforge"), blocked_policy="wait")
    restore(session, before)


def require_ready(session):
    failures = [
        (r.formula, r.status, r.error)
        for r in session.document.formula_results
        if r.status != "ready"
    ]
    assert not failures, failures


def failures(session, first_job):
    return [
        dict(label=j.label, outputs=sorted(j.outputs), error=j.error)
        for j in session.scheduler.jobs[first_job:]
        if j.state == "failed"
    ]


def record_edit(folder, number, key, value, submitted, elapsed, changes, errors):
    record = dict(
        shortcut=key,
        value=value,
        submit_seconds=submitted,
        settle_seconds=elapsed,
        changes={key: row for key, row in changes.items() if max(row.values()) > 1e-9},
        errors=errors,
    )
    (folder / f"edit-{number}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(json.dumps(record), flush=True)


def restore(session, before):
    session.command("undo")
    settled(session)
    differences = delta(session, before)
    assert max(max(row.values()) for row in differences.values()) < 1e-8, differences


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
