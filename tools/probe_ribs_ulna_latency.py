"""Record the real Ribs Top Radius edit without modifying the source project or scheduler."""

import json
import sys
from contextlib import closing
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from time import perf_counter

from qualify_retained_attachment_edits import load

from anthroforge.application import dependencies
from anthroforge.application.session import Session
from anthroforge.core.results import Port


def write(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def job_record(job):
    result = job.describe()
    result.update(
        created=job.created,
        queued_since=job.queued_since,
        ready_at=job.ready_at,
        started=job.started,
        finished=job.finished,
        priority=job.priority,
        interactive=job.interactive,
        provides=[asdict(p) for p in job.provides],
        prerequisites=[asdict(p) for p in job.prerequisites],
    )
    return result


def lineage(session):
    graph = dependencies.graph(session.document)
    ports = dependencies.closure(graph, {Port("SCP_15", "pose")})
    return [dict(port=asdict(p), inputs=[asdict(q) for q in graph.get(p, ())]) for p in ports]


def changes(session, previous, started, output):
    for item in session.document.entities:
        if previous[item.id] != item.matrix:
            output.append(dict(time=perf_counter() - started, id=item.id, name=item.name))
            previous[item.id] = item.matrix


def observe(session, output, started):
    previous = {item.id: item.matrix for item in session.document.entities}
    original = session.scheduler.lifecycle

    def lifecycle(job, phase):
        original(job, phase)
        if phase == "terminal":
            changes(session, previous, started, output)

    session.scheduler.lifecycle = lifecycle


def record(session, output, poses, started, evidence):
    elapsed = perf_counter() - started
    session.command("profile.stop", path=str(output / "edit.afprofile.zip"), wait=True)
    write(output / "poses.json", poses)
    write(output / "jobs.json", [job_record(job) for job in session.scheduler.jobs])
    write(output / "queue.json", evidence)
    write(output / "geometry.json", geometry(session))
    print(json.dumps(dict(seconds=elapsed, errors=session.scheduler.errors)), flush=True)


def geometry(session):
    result = {}
    for item in session.document.registry.records.values():
        asset = getattr(getattr(item, "result", None), "asset", "")
        digest = sha256(repr(getattr(item, "matrix", ())).encode())
        if asset in session.assets:
            for kind in (0, 3):
                digest.update(session.assets[asset].mesh.array(kind).tobytes())
        elif asset in session.resources.paths:
            digest.update(session.resources.paths[asset].path.array().tobytes())
        result[item.id] = digest.hexdigest()
    return result


def capture(session, output):
    from ribs_ulna_queue_probe import monitor, prioritize

    driver = next(d for d in session.document.driving_shortcuts if d.label == "Ribs Top Radius")
    write(output / "ulna-prerequisites.json", lineage(session))
    write(output / "entities.json", [dict(id=e.id, name=e.name) for e in session.document.entities])
    poses, started = [], perf_counter()
    observe(session, poses, started)
    evidence = monitor(session.scheduler)
    if "--priority-probe" in sys.argv:
        prioritize(session.scheduler)
    session.command("profile.start")
    session.command("driver.value", driver=driver.id, value=3.0)
    session.wait(240)
    record(session, output, poses, started, evidence)


def run(source, output):
    output.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        load(session, source)
        capture(session, output)


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:3]))
