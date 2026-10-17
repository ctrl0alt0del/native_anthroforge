"""Real coordinator admission/completion soak with runtime capture and idle measurements."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from standalone_audit import measure

from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.profiling.identity import build_identity
from anthroforge.profiling.service import RuntimeProfiler


def job():
    return Job(
        "Soak",
        frozenset({"fixture"}),
        lambda d: d.revision,
        lambda d, cancel: d,
        lambda result: None,
        kind="attachments",
        interactive=True,
    )


def run(count, recorder):
    now = [0.0]
    scheduler = TaskCoordinator(Document, clock=lambda: now[0])
    scheduler.profiler = recorder
    try:
        start = perf_counter()
        for _ in range(count):
            scheduler.submit(job())
            now[0] += 0.1
            scheduler.wait(timeout=5)
        return results(scheduler, perf_counter() - start)
    finally:
        scheduler.close()


def results(scheduler, elapsed):
    history = scheduler.jobs
    assert not scheduler.active_jobs and all(not j.active for j in history)
    return dict(
        jobs=len(history),
        elapsed_s=elapsed,
        idle_tick=measure(scheduler.tick, 25),
        invalidation=measure(lambda: scheduler.invalidate({"fixture"}), 25),
        retained_snapshots=sum(j.snapshot is not None for j in history),
        retained_cancellations=sum(j.cancel is not None for j in history),
        states={
            state: sum(j.state == state for j in history) for state in {j.state for j in history}
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--jobs", type=int, default=5000)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    profiler = RuntimeProfiler()
    plain = run(args.jobs, None)
    profiler.start()
    recorded = run(args.jobs, profiler)
    profiler.stop(args.output.resolve() / "soak.afprofile.zip", wait=True)
    profiler.close()
    evidence = dict(build=build_identity(), unrecorded=plain, recorded=recorded)
    (args.output / "soak.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
