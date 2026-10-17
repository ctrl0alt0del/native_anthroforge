"""Serial ABBA comparisons against a preserved source/runtime snapshot."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cases():
    for interaction in ("drag", "modal"):
        for opened in (False, True):
            for index, source in enumerate(("baseline", "candidate", "candidate", "baseline")):
                yield interaction, opened, "dormant", index, source
            order = ("candidate", "baseline") if opened else ("baseline", "candidate")
            for index, source in enumerate(order):
                yield interaction, opened, "record", index, source


def command(case, output, events):
    interaction, opened, mode, _, _ = case
    args = [sys.executable, str(ROOT / "tools/profiler_qualification.py"), "--background"]
    args += ["--interaction", interaction, "--mode", mode, "--events", str(events)]
    args += ["--output", str(output)]
    return args + (["--activity-open"] if opened else [])


def measure(case, args):
    interaction, opened, mode, index, source = case
    path = args.output / f"{interaction}-{int(opened)}-{mode}-{index}-{source}.json"
    invoke(case, args, path)
    report = json.loads(path.read_text())
    expected = args.baseline_version if source == "baseline" else args.candidate_version
    assert report["version"] == expected, report["version"]
    print(path.name, [round(t["handler_ms"]["mean"], 2) for t in report["trials"]], flush=True)


def invoke(case, args, path):
    environment = comparison_environment(case[-1], args.baseline)
    with path.with_suffix(".log").open("w") as log:
        result = subprocess.run(
            command(case, path, args.events),
            cwd=ROOT,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
    if result.returncode:
        raise RuntimeError(f"Comparison failed: {path.with_suffix('.log')}")


def comparison_environment(source, baseline):
    return dict(os.environ, PYTHONPATH=str(baseline if source == "baseline" else ROOT / "src"))


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=120)
    parser.add_argument("--baseline-version", default="0.1.4")
    parser.add_argument("--candidate-version", default="0.1.5")
    parser.add_argument("--interaction", choices=("both", "drag", "modal"), default="both")
    parser.add_argument("--activity", choices=("both", "open", "closed"), default="both")
    return parser.parse_args()


def selected_cases(args):
    for case in cases():
        if args.interaction != "both" and case[0] != args.interaction:
            continue
        if args.activity != "both" and case[1] != (args.activity == "open"):
            continue
        yield case


def main():
    args = arguments()
    args.baseline, args.output = args.baseline.resolve(), args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    for case in selected_cases(args):
        measure(case, args)


if __name__ == "__main__":
    main()
