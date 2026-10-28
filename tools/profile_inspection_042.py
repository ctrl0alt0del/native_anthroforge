"""Read-only diagnostic timings on accepted production anatomy, without Qt or recomputation."""

import json
import sys
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

from anthroforge.application.session import Session
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP

OUTPUT = Path("build/inspection-042")


def request(session, operation, status, **options):
    started = perf_counter()
    session.command(operation, **options)
    session.wait(180)
    result = session.command(status)
    assert result["state"] == "ready", result
    return dict(operation=operation, wall_seconds=perf_counter() - started, report=result["report"])


def diagnostics(session):
    ribs, tissue, fiber = targets(session)
    results = [
        request(
            session, "geometry.measure", "geometry.measure.status", target=i.id, plane=[1, 0, 0, 0]
        )
        for i in (ribs, tissue)
    ]
    results.append(binding(session, fiber))
    results.append(
        request(
            session, "geometry.volume", "geometry.volume.status", target=tissue.id, other=ribs.id
        )
    )
    return results


def targets(session):
    anatomy = session.document.registry.anatomy.values()
    ribs = next(i for i in anatomy if i.name == "Ribs")
    tissue = next(
        i for i in anatomy if isinstance(i, TissueVCP) and "Sternocleidomastoid" in i.name
    )
    fiber = next(i for i in session.document.objects if isinstance(i, Fiber) and i.bindings)
    return ribs, tissue, fiber


def binding(session, fiber):
    return request(
        session,
        "geometry.binding",
        "geometry.binding.status",
        target=fiber.id,
        point=fiber.bindings[0].point,
    )


def run(path):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    session = Session()
    try:
        record(session, path)
    finally:
        session.close()


def record(session, path):
    session.command("open", path=path)
    session.wait(180)
    before, cursor = session.document, session.history.cursor
    session.command("profile.start")
    results = diagnostics(session)
    assert session.document is before and session.history.cursor == cursor
    profile = str((OUTPUT / "production.afprofile.zip").resolve())
    session.command("profile.stop", path=profile, wait=True)
    write(results, profile)


def write(results, profile):
    with ZipFile(profile) as archive:
        summary = json.loads(archive.read("summary.json"))
        manifest = json.loads(archive.read("manifest.json"))
    native = {k: v for k, v in summary["durations"].items() if "inspection" in k or "inspect" in k}
    evidence = dict(
        results=results,
        durations=native,
        complete=manifest["complete"],
        geometry_and_bindings_unchanged=True,
        qt_initialized=False,
    )
    (OUTPUT / "production-timings.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(dict(durations=native, complete=manifest["complete"])))


if __name__ == "__main__":
    run(sys.argv[1])
