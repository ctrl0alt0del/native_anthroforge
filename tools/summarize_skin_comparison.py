"""Summarize serial trials and compare saved geometry/bindings without approximating them."""

import json
import statistics
import sys
from pathlib import Path

import numpy as np


def statistics_for(rows, stage, key):
    values = [row[stage][key] for row in rows]
    return dict(median=statistics.median(values), minimum=min(values), maximum=max(values))


def trial_summary(rows):
    seconds = [r["generation_seconds"] for r in rows]
    return dict(
        trials=len(rows),
        seconds=dict(median=statistics.median(seconds), minimum=min(seconds), maximum=max(seconds)),
        peak_rss=statistics_for(rows, "generation_peak", "peak_rss"),
        peak_commit=statistics_for(rows, "generation_peak", "peak_commit"),
        outputs_repeat=all(row["output_hashes"] == rows[0]["output_hashes"] for row in rows),
        stages={name: statistics_for(rows, name, "seconds") for name in stage_names(rows[0])},
    )


def stage_names(row):
    return [
        name
        for name in ("fields", "scene", "envelope", "bindings", "envelope_and_bindings")
        if name in row
    ]


def compare_array(first, second):
    same_shape = first.shape == second.shape
    maximum = float(np.max(np.abs(first - second))) if same_shape and first.size else None
    return dict(
        first_shape=list(first.shape),
        second_shape=list(second.shape),
        exact=bool(np.array_equal(first, second)),
        maximum_error=maximum,
    )


def array_comparison(folder):
    with np.load(folder / "app-1.npz") as app, np.load(folder / "blender-1.npz") as addon:
        names = [key for key in app.files if key in addon.files]
        return {key: compare_array(app[key], addon[key]) for key in names}


def main():
    folder = Path(sys.argv[1])
    groups = {
        name: [json.loads(p.read_text()) for p in sorted(folder.glob(name + "-[0-9].json"))]
        for name in ("app", "blender")
    }
    result = {name: trial_summary(rows) for name, rows in groups.items()}
    result["comparison"] = array_comparison(folder)
    result["capture"] = json.loads((folder / "capture.json").read_text())
    result["precision"] = json.loads((folder / "precision.json").read_text())
    (folder / "comparison.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "capture"}, indent=2))


if __name__ == "__main__":
    main()
