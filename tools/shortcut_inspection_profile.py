"""Serial production-assembly observations and exact geometry/attachment fingerprints."""

import hashlib
import json
import sys
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
from statistics import median
from time import perf_counter

import numpy as np

from qualify_retained_attachment_edits import load
from shortcut_parity_app_capture import record

from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.shortcuts import implicit_identity
from anthroforge.core.tissues import TissueVCP

PLAN = Path("E:/development/WIP_models/shortcut_update_parity_20261023/plan.json")
OUTPUT = Path("build/shortcut-inspection-profile")


def fingerprint(session):
    arrays, frames, metadata = {}, Frames(session.engine, session.document), {}
    for item in session.document.registry.records.values():
        if isinstance(item, (SCP, TissueVCP, Fiber)):
            row = record(session, item, frames, arrays)
            metadata[item.id] = {k: row[k] for k in ("frame", "pose", "attachment") if k in row}
            if isinstance(item, Fiber):
                metadata[item.id]["bindings"] = [asdict(b) for b in item.bindings]
                metadata[item.id]["supports"] = [asdict(s) for s in item.supports]
    geometry = {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in arrays.items()}
    return dict(geometry=geometry, relationships=metadata, connectivity=connectivity(arrays))


def connectivity(arrays):
    result = {}
    for key, faces in arrays.items():
        if key.endswith("__triangles"):
            starts = np.argmin(faces, axis=1)
            indices = (starts[:, None] + np.arange(3)) % 3
            ordered = np.take_along_axis(faces, indices, axis=1)
            ordered = ordered[np.lexsort(ordered.T[::-1])]
            result[key] = hashlib.sha256(ordered.tobytes()).hexdigest()
    return result


def shortcut_key(case):
    mapping = case["mapping"]
    return mapping.get("driver") or implicit_identity(decode_reference(mapping["reference"]))


def inspect_cost(session, key):
    samples = []
    before, cursor = session.document, session.history.cursor
    for _ in range(12):
        start = perf_counter()
        for name in ("effects", "formulas", "attachment_policy", "progress"):
            session.command("shortcut." + name, shortcut=key)
        samples.append((perf_counter() - start) * 1000)
    assert session.document is before and session.history.cursor == cursor
    return dict(median_ms=median(samples), maximum_ms=max(samples), samples_ms=samples)


def edit(session, case):
    mapping = case["mapping"]
    if "driver" in mapping:
        session.command("driver.value", driver=mapping["driver"], value=case["value"])
    else:
        session.command("shortcut.set", reference=mapping["reference"], value=case["value"])
    session.wait(600)


def run(label, case_name):
    plan = json.loads(PLAN.read_text())
    case = next(c for c in plan["cases"] if c["id"] == case_name)
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        result = dict(before=fingerprint(session))
        if label.startswith("candidate"):
            result["inspection"] = inspect_cost(session, shortcut_key(case))
        session.command("profile.start", seconds=120)
        started = perf_counter()
        edit(session, case)
        result.update(edit_seconds=perf_counter() - started, after=fingerprint(session))
        finish(session, result, label, case)


def finish(session, result, label, case):
    prefix = label + "-" + case["id"]
    path = OUTPUT / (prefix + ".afprofile.zip")
    session.command("profile.stop", path=str(path.resolve()), wait=True)
    if label.startswith("candidate"):
        result["progress"] = session.command("shortcut.progress", shortcut=shortcut_key(case))
    result["errors"] = session.scheduler.errors
    (OUTPUT / (prefix + ".json")).write_text(json.dumps(result))
    print(prefix, result["edit_seconds"], result.get("inspection", {}).get("median_ms"), flush=True)


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    run(sys.argv[1], sys.argv[2])
