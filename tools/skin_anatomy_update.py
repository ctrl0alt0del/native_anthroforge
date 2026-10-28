"""Qualify fixed skin topology and isolated fitting on an existing anatomical assembly."""

import argparse
import json
from pathlib import Path
from time import perf_counter, sleep

import numpy as np

from anthroforge.application import storage
from anthroforge.application.preferences import PreferenceStore
from anthroforge.application.session import Session
from anthroforge.native import topology


def settle(session, start):
    next_report = 0
    while session.scheduler.active_jobs:
        session.scheduler.tick()
        if perf_counter() > next_report:
            active = [job.describe() for job in session.scheduler.active_jobs]
            print(json.dumps(dict(active=active)), flush=True)
            next_report = perf_counter() + 30
        sleep(0.01)
    failed = [j.error for j in session.scheduler.jobs[start:] if j.state == "failed"]
    assert not failed, failed


def operation(session, report, label, name, **arguments):
    start, clock = len(session.scheduler.jobs), perf_counter()
    result = session.command(name, **arguments)
    settle(session, start)
    report[label] = dict(seconds=perf_counter() - clock, result=result)
    print(json.dumps({label: report[label]}), flush=True)
    return result


def deform(session, args, report, driver):
    reference = session.document.skin.reference
    before = session.assets[session.document.skin.final.asset].mesh
    operation(session, report, "update", "driver.value", driver=driver.id, value=args.value)
    session.skin_status.require("fit")
    after = session.assets[session.document.skin.final.asset].mesh
    assert session.document.skin.reference == reference and topology.same_topology(before, after)
    displacement = np.linalg.norm(after.array(0) - before.array(0), axis=1)
    report["displacement"] = dict(
        maximum=float(displacement.max()), mean=float(displacement.mean())
    )
    assert report["displacement"]["maximum"] > 0
    storage.atomic_save(args.output / "updated.anthroforge", session.document, session.resources)


def fit(session, args, report, driver):
    before = session.document
    settings = fit_settings(driver.value, args.value)
    operation(session, report, "fit", "skin.fit", shortcut=driver.id, settings=settings)
    assert (
        session.document.entities == before.entities and session.document.objects == before.objects
    )
    assert session.document.skin.final == before.skin.final
    item = session.document.skin.fits[-1]
    report["fit_metadata"] = json.loads(session.resources.skin[item.data].metadata)
    preview(session, report, item.id, (driver.value + args.value) / 2)
    storage.atomic_save(args.output / "fitted.anthroforge", session.document, session.resources)


def fit_settings(left, right):
    return dict(minimum=min(left, right), maximum=max(left, right), bones=4, samples=5)


def preview(session, report, identity, value):
    before, jobs = session.document, len(session.scheduler.jobs)
    operation(session, report, "preview", "skin.fit.preview", identity=identity, value=value)
    assert session.document is before
    assert all(job.key == "skin-fit-preview" for job in session.scheduler.jobs[jobs:])
    assert session.command("skin.fit.preview.status")["visible"]
    session.command("skin.fit.preview.cancel")


def run(session, args, report):
    session.command("open", path=str(args.project))
    settle(session, 0)
    session.skin_status.require("fit")
    driver = next(d for d in session.document.driving_shortcuts if d.label == args.driver)
    report["driver"] = dict(id=driver.id, label=driver.label, before=driver.value, after=args.value)
    session.command("profile.start", seconds=3600)
    try:
        deform(session, args, report, driver)
        if args.fit:
            fit(session, args, report, driver)
        report["success"] = True
    finally:
        session.command("profile.stop", path=str(args.output / "update.afprofile.zip"), wait=True)


def options():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--driver", default="Ribs Top Radius")
    parser.add_argument("--value", type=float, default=1.05)
    parser.add_argument("--fit", action="store_true")
    result = parser.parse_args()
    result.output.mkdir(parents=True, exist_ok=True)
    return result


def main():
    args, session = options(), Session(preferences=PreferenceStore())
    report = dict(source=str(args.project), success=False)
    try:
        run(session, args, report)
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        storage.atomic_save(
            args.output / "retained.anthroforge", session.document, session.resources
        )
        (args.output / "evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        session.close()


if __name__ == "__main__":
    main()
