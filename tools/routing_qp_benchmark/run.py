"""Serial, counterbalanced complete routes; assembly and solver setup are timed."""

import argparse
import hashlib
import json
import platform
import subprocess
from dataclasses import replace
from itertools import permutations
from pathlib import Path

from anthroforge.native import routing, routing_scene
from tools.profiler_system_load import system_load, system_times

from . import cases, harness


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rounds", type=int, default=12)
    parser.add_argument("--filter", default="")
    parser.add_argument("--skull", action="store_true")
    parser.add_argument("--backends", default="0,1,2")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--audit", action="store_true")
    return parser.parse_args()


def warm_input(engine, spec, path, mode):
    engine.clear_caches()
    if mode == "cold":
        return spec
    routing_scene.capture(engine, routing.arrays(spec), spec.curve.engine_settings.radius, 0)
    return replace(spec, warm=path)


def checked(engine, spec, case):
    path, result = harness.measure(engine, spec)
    if path is not None:
        quality = harness.quality(engine, path, spec, case)
        result["quality"] = {k: v for k, v in quality.items() if k not in ("points", "parameters")}
        assert quality["clear"] and quality["finite"] and quality["monotonic"], case["name"]
        assert quality["pin_error"] < 1e-12, case["name"]
    return path, result


def trial(engine, spec, path, case, backend, mode, args):
    value = warm_input(engine, spec, path, mode)
    harness.configure(engine, backend, tolerance=args.tolerance)
    _, result = checked(engine, value, case)
    return dict(result, backend=backend, mode=mode)


def timings(engine, spec, path, case, args):
    backends = [int(v) for v in args.backends.split(",")]
    orders, results = list(permutations(backends)), []
    for index in range(args.rounds):
        for mode in ("cold", "warm") if index % 2 == 0 else ("warm", "cold"):
            for slot, backend in enumerate(orders[index % len(orders)]):
                row = trial(engine, spec, path, case, backend, mode, args)
                results.append(dict(row, round=index, slot=slot))
    return results


def audit(engine, spec, case, args):
    engine.clear_caches()
    harness.configure(engine, 0, paired=True, audit=True, tolerance=args.tolerance)
    path, result = checked(engine, spec, case)
    return dict(result, records=harness.records(engine))


def run_case(engine, case, args):
    meshes, spec = cases.inputs(engine, case)
    harness.configure(engine, 0)
    path, baseline = checked(engine, spec, case)
    assert path is not None, baseline
    load = system_times()
    result = dict(name=case["name"], samples=case["samples"], surfaces=len(meshes))
    result["triangles"] = sum(len(s["triangles"]) for s in case["surfaces"])
    result["trials"] = timings(engine, spec, path, case, args)
    result["load"] = system_load(load)
    if args.audit:
        result["audit"] = audit(engine, spec, case, args)
    engine.clear_caches()
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance(args):
    source = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=cases.ROOT, text=True
    ).strip()
    fixtures = {p.name: digest(p) for p in cases.FIXTURES.glob("*.json")}
    if args.skull:
        fixtures["skull-routing-inputs.json"] = digest(
            cases.ROOT / "build/skull-routing-inputs.json"
        )
    return dict(source=source, library=digest(harness.LAB), fixtures=fixtures)


def metadata(args):
    return dict(
        platform=platform.platform(),
        python=platform.python_version(),
        **provenance(args),
        tolerance=args.tolerance,
        rounds=args.rounds,
        backends=args.backends,
        audit=args.audit,
        warm="Same accepted baseline path; no authored edit; scene cache prepared before timing",
        timing="Whole native routing including preparation, scene capture, planning and validation",
    )


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2))


def main():
    args, engine = arguments(), harness.engine()
    report = dict(metadata=metadata(args), cases=[])
    selected = [c for c in cases.all_cases(args.skull) if args.filter in c["name"]]
    for case in selected:
        report["cases"].append(run_case(engine, case, args))
        save(args.output, report)
        print(f"Completed {case['name']} ({len(report['cases'])}/{len(selected)})", flush=True)
    print(args.output)


if __name__ == "__main__":
    main()
