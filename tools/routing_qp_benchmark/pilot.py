"""Qualify baseline identity and full-backend feasibility before timing experiments."""

import argparse
import json

import numpy as np

from anthroforge.native.mesh import GeometryEngine

from . import cases, harness


def trial(engine, case, backend, audit=True):
    meshes, spec = cases.inputs(engine, case)
    if hasattr(engine.library, "af_route_lab_configure"):
        harness.configure(engine, backend, audit=audit)
    path, result = harness.measure(engine, spec)
    if path is not None:
        result["quality"] = harness.quality(engine, path, spec, case)
    result["records"] = harness.records(engine) if audit else []
    engine.clear_caches()
    return result


def parity(reference, current):
    assert reference["ok"] == current["ok"]
    if not reference["ok"]:
        return
    assert reference["counters"] == current["counters"]
    np.testing.assert_array_equal(reference["quality"]["points"], current["quality"]["points"])
    np.testing.assert_array_equal(
        reference["quality"]["parameters"], current["quality"]["parameters"]
    )


def run_case(engine, production, case):
    reference = trial(production, case, 0, audit=False)
    rows = [trial(engine, case, backend) for backend in range(3)]
    parity(reference, rows[0])
    print(
        case["name"],
        [(r["ok"], round(r["wall_ms"], 2), r.get("counters")) for r in rows],
        flush=True,
    )
    return dict(case=case["name"], production=reference, results=rows, baseline_identical=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", default="")
    parser.add_argument("--skull", action="store_true")
    args = parser.parse_args()
    engine, production = harness.engine(), GeometryEngine()
    selected = [c for c in cases.all_cases(args.skull) if args.filter in c["name"]]
    output = [run_case(engine, production, case) for case in selected]
    path = cases.ROOT / "build/routing-piqp/pilot.json"
    path.write_text(json.dumps(output, indent=2))
    print(path)


if __name__ == "__main__":
    main()
