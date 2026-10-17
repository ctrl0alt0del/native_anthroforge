"""Read-only scaling experiments for the 0.1.5 standalone architecture audit."""

import argparse
import cProfile
import json
from dataclasses import replace
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

import numpy as np

from anthroforge.application import dependencies
from anthroforge.application.coordinator import TaskCoordinator
from anthroforge.application.history import History
from anthroforge.application.primitive_operations import default_primitive
from anthroforge.application.session import Session
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.jobs import Job
from anthroforge.desktop.scene_state import records
from anthroforge.profiling.identity import build_identity


def measure(call, repeats=9):
    values = []
    for _ in range(repeats):
        start = perf_counter()
        call()
        values.append((perf_counter() - start) * 1000)
    return dict(
        mean_ms=float(np.mean(values)), median_ms=float(np.median(values)), samples_ms=values
    )


def document_fixture(count, mode="MANUAL"):
    root = SCP("Root", id="root")
    others = tuple(SCP(str(i), id=str(i), parent=root.id) for i in range(count - 2))
    body = SCP("Body", id="body", parent=root.id, primitive=default_primitive("BODY", "CAPSULE"))
    return Document(entities=(root, *others, body), update_mode=mode)


def document_scaling(count):
    document = document_fixture(count)
    return dict(
        entities=count,
        replace_revision=measure(lambda: replace(document, revision=1)),
        dependency_graph=measure(lambda: dependencies.graph(document)),
        scene_projection=projection_cost(document),
        manual_point_edit=edit_cost(document),
        live_point_admission=edit_cost(replace(document, update_mode="LIVE")),
    )


def edit_cost(document):
    session = Session()
    session.document, session.history = document, History(document)
    session.scheduler.checkpoint = document
    session.begin()
    edit = point_editor(session)
    try:
        edit()
        return measure(edit)
    finally:
        session.close()


def point_editor(session):
    curve = session.document.entity("body").primitive.curves[0]
    target = dict(entity="body", curve=curve.id, point=curve.points[0].id)
    count = 0

    def edit():
        nonlocal count
        count += 1
        session.command("point.update", **target, position=[-0.5, count * 0.001, 0])

    return edit


def projection_cost(document):
    session = Session()
    session.document = document
    controller = SimpleNamespace(session=session)
    try:
        records(controller)
        return measure(lambda: records(controller))
    finally:
        session.close()


def completed_job(index, document):
    job = Job("Finished", frozenset(), lambda d: d, lambda d, c: None, lambda r: None)
    job.id, job.state, job.snapshot = str(index), "succeeded", document
    return job


def job_scaling(count):
    document = Document()
    coordinator = TaskCoordinator(lambda: document)
    coordinator.jobs = [completed_job(i, document) for i in range(count)]
    try:
        return dict(
            completed_jobs=count,
            idle_tick=measure(coordinator.tick, 25),
            invalidate=measure(lambda: coordinator.invalidate_ports(set()), 25),
        )
    finally:
        coordinator.close()


def command_profile(output):
    session = Session()
    session.document = document_fixture(512, "LIVE")
    session.history = History(session.document)
    session.begin()
    edit = point_editor(session)
    edit()
    profile = cProfile.Profile()
    try:
        profile.runcall(edit)
        profile.dump_stats(str(output / "point-admission.pstats"))
    finally:
        session.close()


def runtime_profile(output):
    session = Session()
    session.document = document_fixture(1024, "LIVE")
    session.history = History(session.document)
    session.begin()
    edit = point_editor(session)
    edit()
    try:
        path = str((output / "admission.afprofile.zip").resolve())
        session.command("profile.start")
        for _ in range(9):
            edit()
        session.command("profile.stop", path=path, wait=True)
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = dict(
        build=build_identity(), scope="Synthetic star hierarchy; no GUI or worker dispatch"
    )
    result["document"] = [document_scaling(n) for n in (16, 64, 256, 1024)]
    result["jobs"] = [job_scaling(n) for n in (0, 1000, 10000, 50000)]
    command_profile(args.output)
    runtime_profile(args.output)
    (args.output / "scaling.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
