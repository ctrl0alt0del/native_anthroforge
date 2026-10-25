"""Production assembly staging profile; no window, GPU/frame-latency or speedup claims."""

import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

from PySide6.QtCore import QCoreApplication
from qualify_retained_attachment_edits import load

from anthroforge.desktop.controller import Controller


def fingerprints(session):
    meshes = {
        key: (value.mesh.array(0), value.mesh.array(1), value.mesh.array(2))
        for key, value in session.assets.items()
    }
    paths = {
        key: (value.path.array(), value.path.array(1))
        for key, value in session.resources.paths.items()
    }
    return {"meshes": hashes(meshes), "paths": hashes(paths)}


def hashes(rows):
    return {
        key: [hashlib.sha256(array).hexdigest() for array in arrays] for key, arrays in rows.items()
    }


def stage(controller):
    started = perf_counter()
    controller.refresh()
    prepared = perf_counter()
    controller.session.wait(180)
    computed = perf_counter()
    drain(controller)
    return dict(
        preparation_ms=(prepared - started) * 1000,
        work_ms=(computed - prepared) * 1000,
        staging_ms=(perf_counter() - computed) * 1000,
    )


def drain(controller):
    for _ in range(10000):
        for model in controller.geometry_models():
            model.drain()
        controller.frame_presented()
        if not any(model.pending for model in controller.geometry_models()):
            break
    controller.frame_presented()


def qualify(controller, source, output):
    load(controller.session, source)
    assert all(
        p.path.engine is controller.session.engine
        for p in controller.session.resources.paths.values()
    )
    before = fingerprints(controller.session)
    document, cursor = controller.session.document, controller.session.history.cursor
    controller.session.command("profile.start")
    timing = stage(controller)
    assert controller.session.document == document and controller.session.history.cursor == cursor
    assert fingerprints(controller.session) == before
    return finish(controller, output, timing)


def finish(controller, output, timing):
    result = controller.session.command(
        "profile.stop", path=str(output / "display.afprofile.zip"), wait=True
    )
    assert result["state"] == "saved", result
    jobs = [j for j in controller.session.scheduler.jobs if j.kind == "fiber_display"]
    assert jobs and all(j.state == "succeeded" and not j.writes for j in jobs), [
        (j.state, j.error) for j in jobs
    ]
    verify_report(result["path"], len(jobs))
    return summary(controller, timing, jobs, result)


def verify_report(path, count):
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        summary = json.loads(archive.read("summary.json"))
    assert manifest["complete"] and not manifest["losses"]
    assert summary["durations"]["native/af_path_display_tube"]["count"] == count


def summary(controller, timing, jobs, result):
    return dict(
        timing=timing,
        jobs=len(jobs),
        displayed=len(controller.fiber_display.model.active_rows()),
        geometry_unchanged=True,
        attachment_records_unchanged=True,
        profiler=result["path"],
        scope="CPU preparation, worker and staging; no GPU or physical frame-latency claim",
    )


def run(source, output):
    output.mkdir(parents=True, exist_ok=True)
    controller = Controller()
    controller.timer.stop()
    try:
        result = qualify(controller, source, output)
        (output / "qualification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result))
    finally:
        controller.close()


if __name__ == "__main__":
    app = QCoreApplication([])
    run(Path(sys.argv[1]), Path(sys.argv[2]))
