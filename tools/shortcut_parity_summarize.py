"""Summarize measured differences without turning queue completion into acceptance."""

import sys
from collections import Counter
from pathlib import Path

from shortcut_parity_compare import compare_object, dataset
from shortcut_parity_plan import read, write

from anthroforge.native.mesh import GeometryEngine


def compact(row):
    keys = ("id", "name", "kind", "source_crop", "changed", "pose_comparison_skipped")
    result = {key: row[key] for key in keys if key in row}
    for name in ("surface_distance", "pose_aligned_distance", "indexed_path_distance"):
        if name in row:
            result[name] = row[name]["max"]
    if "endpoints" in row:
        result["endpoint_response_error"] = max(row["endpoints"]["response"])
    return result


def affected(rows, kind):
    return [
        row
        for row in rows
        if row["kind"] == kind
        and not row["mirror"]
        and not row.get("unavailable")
        and any(row.get("changed", {}).values())
    ]


def largest(rows, metric):
    selected = [r for r in rows if metric in r]
    return [compact(r) for r in sorted(selected, key=lambda r: r[metric]["max"], reverse=True)[:8]]


def case_summary(folder, case):
    data = read(folder / (case + "-comparison.json"))
    return dict(
        case=case,
        addon_runtime=data["addon_runtime"],
        app_errors=data["app_errors"],
        **summary_rows(data["rows"]),
    )


def summary_rows(rows):
    fibers = [r for r in rows if "endpoints" in r]
    worst = sorted(fibers, key=lambda r: max(r["endpoints"]["response"]), reverse=True)
    return dict(
        counts=dict(Counter(r["kind"] for r in rows)),
        affected_counts={k: len(affected(rows, k)) for k in ("SCP", "TissueVCP")},
        affected_bones=largest(affected(rows, "SCP"), "surface_distance"),
        affected_tissues=largest(affected(rows, "TissueVCP"), "surface_distance"),
        fiber_endpoints=[compact(r) for r in worst[:8]],
        unavailable=[r for r in rows if r.get("unavailable")],
    )


def donor_case(engine, folder, case):
    initial = dataset(folder, "app", "baseline"), dataset(folder, "fds-donor", "baseline")
    app, blender = dataset(folder, "app", case), dataset(folder, "fds-donor", case)
    keys = [k for k, row in blender[0]["lookup"].items() if row["kind"] != "SCP"]
    rows = [compare_object(engine, k, app, blender, initial) for k in keys]
    write(folder / (case + "-fds-comparison.json"), dict(case=case, rows=rows))
    return dict(case=case, failures=[r for r in rows if r.get("addon_error")])


def refresh_probe(engine, folder):
    initial = dataset(folder, "app", "baseline"), dataset(folder, "blender", "baseline")
    app = dataset(folder, "app", "SHORTCUT_16")
    key = "a73b36a6-ac93-42b9-bb00-c111393285c0"
    results = {}
    for case in ("SHORTCUT_16", "SHORTCUT_16-refresh"):
        addon = dataset(folder, "blender", case)
        results[case] = compare_object(engine, key, app, addon, initial)
    write(folder / "radius-refresh-comparison.json", results)
    return {key: compact(row) for key, row in results.items()}


def summary(engine, folder, plan):
    cases = ["baseline"] + [c["id"] for c in plan["cases"]]
    return dict(
        schema=1,
        overall_parity=False,
        requested=plan["cases"],
        units="metres under source scene scale 1; addon root has no physical-unit declaration",
        source_groups=len(plan["groups"]),
        selected_muscles=len(plan["records"]),
        cases=[case_summary(folder, c) for c in cases],
        original_fds=[donor_case(engine, folder, c) for c in cases],
        radius_refresh=refresh_probe(engine, folder),
        **probes(folder),
    )


def probes(folder):
    return dict(
        humerus_counterfactual=read(folder / "owner-binding-counterfactual.json"),
        thumb_counterfactual=read(folder / "SHORTCUT_21-owner-probe.json"),
        source_mesh_preservation=read(folder / "authored-only.json"),
    )


if __name__ == "__main__":
    output = Path(sys.argv[1])
    write(output / "summary.json", summary(GeometryEngine(), output, read(output / "plan.json")))
