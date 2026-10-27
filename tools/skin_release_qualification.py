"""Public skin stages on a captured project; logs evidence without modifying its source."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter, sleep

from anthroforge.application import storage
from anthroforge.application.preferences import PreferenceStore
from anthroforge.application.session import Session
from anthroforge.core import skin_sources


def write_report(output, report):
    (output / "evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def wait(session, job):
    last = 0
    while job.active:
        session.scheduler.tick()
        if perf_counter() - last > 30:
            print(json.dumps(job.describe()), flush=True)
            last = perf_counter()
        sleep(0.01)
    if job.state != "succeeded":
        raise ValueError(job.error or job.state)


def stage(session, operation, output, report):
    started = perf_counter()
    session.command("profile.start", seconds=3600)
    try:
        identity = session.command(operation)
        job = session.scheduler.registry.by_id[identity]
        wait(session, job)
        report[operation] = dict(seconds=perf_counter() - started, job=job.describe())
        save_stage(session, operation, output)
    finally:
        finish_capture(session, operation, output, report)


def finish_capture(session, operation, output, report):
    save_stage(session, "retained", output)
    name = operation.replace(".", "-")
    session.command("profile.stop", path=str(output / (name + ".afprofile.zip")), wait=True)
    write_report(output, report)


def save_stage(session, operation, output):
    name = operation.replace(".", "-")
    storage.atomic_save(output / (name + ".anthroforge"), session.document, session.resources)
    for kind in ("envelope", "topology", "final"):
        stage = getattr(session.document.skin, kind)
        if stage.asset:
            print(
                json.dumps(dict(stage=kind, counts=session.assets[stage.asset].mesh.counts)),
                flush=True,
            )


def run(session, options, report):
    started = perf_counter()
    session.command("open", path=str(options.project))
    session.wait()
    report["open_seconds"] = perf_counter() - started
    report["contributors"] = len(skin_sources.contributors(session.document))
    report["anatomy"] = len(session.document.registry.anatomy)
    report["source_revision"] = session.document.revision
    write_report(options.output, report)
    print(json.dumps(report), flush=True)
    for operation in options.operations:
        stage(session, operation, options.output, report)


def options():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--operations", nargs="+", default=["skin.build"])
    result = parser.parse_args()
    result.output.mkdir(parents=True, exist_ok=True)
    return result


def main():
    args = options()
    report = dict(source=str(args.project), success=False)
    report["sha256"] = hashlib.file_digest(args.project.open("rb"), "sha256").hexdigest()
    session = Session(preferences=PreferenceStore())
    try:
        run(session, args, report)
        report["success"] = True
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        write_report(args.output, report)
        session.close()


if __name__ == "__main__":
    main()
