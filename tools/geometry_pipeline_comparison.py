"""Compare the production evaluator with a pinned previous evaluator, serially."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from standalone_audit import measure
from standalone_geometry_audit import changed_entity, evaluator, fixture, verify_geometry

from anthroforge.application.session import Session
from anthroforge.profiling.identity import build_identity


def previous_evaluator(path):
    spec = importlib.util.spec_from_file_location(
        "anthroforge.application._previous_evaluator", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Evaluation


def compare(session, previous_type, samples, sides):
    entity, previous, cancel = fixture(session, samples, sides)
    worker = evaluator(session, entity, previous, cancel)
    old = previous_type(session.engine, worker.document, worker.meshes, cancel)
    for step in range(8):
        item = changed_entity(entity, step)
        verify_geometry(old.geometry(item), worker.geometry(item))
    calls = {"baseline": lambda: old.geometry(entity), "candidate": lambda: worker.geometry(entity)}
    runs = [
        dict(mode=mode, **measure(calls[mode], 12))
        for mode in ("baseline", "candidate", "candidate", "baseline")
    ]
    return dict(samples=samples, sides=sides, vertices=previous.counts[0], runs=runs)


def record(session, output):
    entity, previous, cancel = fixture(session, 32, 16)
    worker = evaluator(session, entity, previous, cancel)
    session.engine.bases.clear()
    session.command("profile.start")
    for step in range(5):
        worker.geometry(changed_entity(entity, step))
    session.command(
        "profile.stop", path=str(output.resolve() / "geometry.afprofile.zip"), wait=True
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        old = previous_evaluator(args.baseline)
        results = [compare(session, old, n, s) for n, s in ((32, 16), (128, 32), (256, 64))]
        record(session, args.output)
        save_results(args, results)
    finally:
        session.close()


def save_results(args, results):
    evidence = dict(
        build=build_identity(),
        baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        runs=results,
    )
    (args.output / "comparison.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
