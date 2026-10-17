"""Summarize serial Activity comparisons without summing nested profiler durations."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from zipfile import ZipFile


def load_run(path):
    report = json.loads(path.read_text())
    return dict(
        file=path.name,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        version=report["version"],
        activity_open=report["activity_open"],
        interaction=report["interaction"],
        mode=report["mode"],
        system_load=report["system_load"],
        trials=[trim_trial(trial) for trial in report["trials"]],
    )


def trim_trial(trial):
    keys = ("snapping", "snap_hits", "events", "handler_ms", "frame_ms", "jobs")
    return {key: trial[key] for key in keys}


def comparisons(runs):
    results = []
    for interaction in ("drag", "modal"):
        for opened in (False, True):
            matching = [r for r in runs if r["interaction"] == interaction]
            matching = [r for r in matching if r["activity_open"] == opened]
            for snap in (False, True):
                result = paired_result(matching, snap)
                results.append(dict(interaction=interaction, activity_open=opened, **result))
    return results


def paired_result(runs, snapping):
    groups = {}
    for version in ("0.1.4", "0.1.5"):
        trials = [
            r["trials"][int(snapping)]
            for r in runs
            if r["version"] == version and r["mode"] == "dormant"
        ]
        groups[version] = trial_distribution(trials)
    improvement = 1 - groups["0.1.5"]["handler_mean_ms"] / groups["0.1.4"]["handler_mean_ms"]
    return dict(snapping=snapping, versions=groups, handler_reduction_percent=100 * improvement)


def trial_distribution(trials):
    values = [trial["handler_ms"]["mean"] for trial in trials]
    frames = [trial["frame_ms"]["mean"] for trial in trials]
    return dict(
        handler_mean_ms=mean(values),
        handler_mean_range_ms=values,
        frame_callback_mean_ms=mean(frames),
    )


def load_profile(path):
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        summary = json.loads(archive.read("summary.json"))
        trace = json.loads(archive.read("trace.json"))["traceEvents"]
    result = dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    keys = ("environment", "complete", "losses", "storage", "requested_interval_ns", "profiler")
    result.update({key: manifest[key] for key in keys})
    result.update(
        {key: summary[key] for key in ("retained_interval_us", "frame_submission_intervals")}
    )
    result["activity_model_events"] = activity_events(trace)
    result["selected_durations"] = selected_durations(summary)
    return result


def activity_events(trace):
    counts = Counter()
    for event in trace:
        args = event.get("args", {})
        activity = args.get("source") == "Activity.qml" or args.get("class") == "ActivityModel"
        if event.get("cat") == "model" and activity:
            counts[event["name"]] += 1
    return dict(counts)


def selected_durations(summary):
    return {
        key: value
        for key, value in summary["durations"].items()
        if "Activity.qml" in key
        or key in ("ui/Controller.notify", "native/af_scene_pick", "native/af_surface_normal")
    }


def methodology():
    return dict(
        fixture="examples/primitives/cube.obj plus Body primitive; 120 moves per gesture",
        sequence="Serial baseline/candidate/candidate/baseline for each unrecorded condition",
        sources="0.1.4 at 3fa664d; 0.1.5 production at a4501be; same native binaries",
        recordings="One baseline and candidate recording per condition; order alternates",
        display="1500x950 nonactivating window, DPR 1.5, Windows 11; no parallel test/build",
        handler="Synchronous input handling; excludes OS queue wait and physical input latency",
        frames="GUI receipt of frameSwapped; not physical display or GPU execution time",
        retention="128 MiB owned budget; complete means clean stop, not zero ring eviction",
        limits="Two unrecorded repeats; normal then Ctrl; background/thermal state uncontrolled",
        overlap="Profiler inclusive spans overlap; do not sum or subtract collector costs",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--confirmation", type=Path)
    args = parser.parse_args()
    result = build_evidence(args)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def build_evidence(args):
    runs = [load_run(path) for path in sorted(args.directory.glob("*.json"))]
    profiles = [load_profile(path) for path in sorted(args.directory.glob("*.afprofile.zip"))]
    result = dict(
        methodology=methodology(), runs=runs, comparisons=comparisons(runs), profiles=profiles
    )
    if args.confirmation:
        result["final_confirmation"] = [
            load_run(p) for p in sorted(args.confirmation.glob("*.json"))
        ]
    return result


if __name__ == "__main__":
    main()
