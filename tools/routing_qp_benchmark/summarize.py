"""Compact, shareable evidence; diagnostic times are separate from uninstrumented trials."""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev


def distribution(values):
    data = sorted(values)
    if not data:
        return {}
    return dict(
        count=len(data),
        median=median(data),
        mean=mean(data),
        p10=data[int((len(data) - 1) * 0.1)],
        p90=data[int((len(data) - 1) * 0.9)],
        min=data[0],
        max=data[-1],
        cv=pstdev(data) / mean(data) if mean(data) else 0,
    )


def group_trials(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row["mode"], row["backend"])].append(row)
    return [summarize_group(mode, backend, values) for (mode, backend), values in groups.items()]


def summarize_group(mode, backend, rows):
    successful = [row for row in rows if row["ok"]]
    return dict(
        mode=mode,
        backend=backend,
        failures=len(rows) - len(successful),
        invalid_results=sum(not r["quality"]["clear"] for r in successful),
        wall_ms=distribution([r["wall_ms"] for r in rows]),
        cpu_ms=distribution([r["cpu_ms"] for r in rows]),
        counters=successful[0]["counters"] if successful else None,
        quality=successful[0]["quality"] if successful else None,
    )


def matched_rows(records):
    groups = defaultdict(list)
    for row in records:
        groups[row["step"]].append(row)
    result = defaultdict(list)
    for rows in groups.values():
        assert len(rows) == 7, "Expected six paired comparisons and one continuing solve"
        for row in rows[:6]:
            result[int(row["backend"])].append(row)
    return result


def finite_values(rows, key):
    return [r[key] for r in rows if r[key] is not None and math.isfinite(r[key])]


def diagnostic(backend, rows):
    result = dict(
        backend=backend,
        count=len(rows),
        failures=sum(r["status"] != 1 for r in rows),
        incomplete_duals=sum(not r["dual_valid"] for r in rows),
        max_contacts=max(r["contacts"] for r in rows),
        max_points=max(r["points"] for r in rows),
        reuse_fraction=mean(r["reused"] for r in rows),
    )
    for key in ("total_ms", "assembly_ms", "prepare_ms", "solve_ms", "primal", "stationarity"):
        result[key] = distribution(finite_values(rows, key))
    result["sum_candidate_ms"] = sum(r["total_ms"] for r in rows) / 2
    return result


def summarize_case(case):
    result = {k: case[k] for k in ("name", "samples", "surfaces", "triangles", "load")}
    result["groups"] = group_trials(case["trials"])
    if "audit" in case:
        matched = matched_rows(case["audit"]["records"])
        result["matched_qps"] = [diagnostic(k, v) for k, v in sorted(matched.items())]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.source.read_text())
    result = dict(metadata=report["metadata"], cases=[summarize_case(c) for c in report["cases"]])
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False))
    print(args.output)


if __name__ == "__main__":
    main()
