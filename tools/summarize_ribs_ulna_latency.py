"""Extract dependency waiting and runnable queue delay from the captured experiment."""

import json
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def events(folder):
    with ZipFile(folder / "edit.afprofile.zip") as archive:
        return json.loads(archive.read("trace.json"))["traceEvents"]


def selected(jobs, target, kind):
    return next(
        j
        for j in reversed(jobs)
        if target in j["outputs"] and j["state"] == "succeeded" and j["scheduling"]["kind"] == kind
    )


def eligible(folder, job):
    rows = [
        r
        for r in read(folder / "queue.json")
        for t in r["targets"]
        if t["id"] == job["id"] and not t["blockers"] and r["time"] >= t["ready"]
    ]
    return rows[0]["time"] if rows else None


def stages(trace, job):
    return {
        e["name"]: e["dur"] / 1000
        for e in trace
        if e.get("cat") == "task"
        and e.get("ph") == "X"
        and e.get("args", {}).get("job") == job["id"]
    }


def intervening(jobs, start, end):
    return Counter(
        j["scheduling"]["kind"]
        for j in jobs
        if start < j["started"] < end and j["state"] == "succeeded"
    )


def timeline(ulna, radius, formula, start, ready):
    return dict(
        radius_s=radius["finished"] - start,
        formula_s=formula["finished"] - start,
        ulna_eligible_s=ready - start if ready else None,
        ulna_start_s=ulna["started"] - start,
        ulna_publish_s=ulna["finished"] - start,
        runnable_wait_ms=(ulna["started"] - ready) * 1000 if ready else None,
        after_formula_ms=(ulna["started"] - formula["finished"]) * 1000,
    )


def summarize(folder):
    jobs, trace = read(folder / "jobs.json"), events(folder)
    start = next(
        (e["ts"] / 1e6 for e in trace if e.get("cat") == "command" and e["name"] == "driver.value"),
        None,
    )
    if start is None:
        return dict(trial=folder.name, incomplete=True, reason="Initial command was evicted.")
    ulna, radius = selected(jobs, "SCP_15", "attachments"), selected(jobs, "SCP_14", "attachments")
    formula, ready = selected(jobs, "SCP_15", "formulas"), eligible(folder, ulna)
    result = timeline(ulna, radius, formula, start, ready)
    result.update(trial=folder.name, ulna_stages_ms=stages(trace, ulna))
    result["intervening_jobs"] = intervening(jobs, ready or ulna["started"], ulna["started"])
    return result


def run(root):
    rows = [
        summarize(p)
        for p in root.iterdir()
        if (p / "edit.afprofile.zip").exists() and (p / "queue.json").exists()
    ]
    (root / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
