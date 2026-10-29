"""Serial old/new painting parity and timing; run separately against each checkout."""

import argparse
import hashlib
import json
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from profiler_system_load import system_load, system_times

from anthroforge.application import projects, storage, surface_providers
from anthroforge.application.session import Session
from anthroforge.core.tissues import TissueVCP
from tests.test_tissue_painting_native import VIEW


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--new", action="store_true")
    parser.add_argument("--profile", action="store_true")
    return parser.parse_args()


def load(session, args):
    fingerprint = digest(args.project)
    if args.project:
        document, resources = storage.read_package(args.project, session.engine)
        projects.adopt(session, document, resources)
    else:
        create_grid(args.output / "dense.obj")
        session.command("import", path=str(args.output / "dense.obj"), units=1)
        session.wait()
    return fingerprint


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else ""


def create_grid(path, width=257):
    with path.open("w") as stream:
        for y in range(width):
            for x in range(width):
                stream.write(f"v {x / (width - 1) - 0.5} {y / (width - 1) - 0.5} 0\n")
        for y in range(width - 1):
            for x in range(width - 1):
                a = y * width + x + 1
                stream.write(f"f {a} {a + 1} {a + width + 1} {a + width}\n")


def largest(session, records):
    valid = [r for r in records if r.result.asset in session.assets]
    return max(valid, key=lambda r: session.assets[r.result.asset].mesh.counts[0])


def cases(session):
    bone = largest(session, session.document.entities)
    session.command("skin.collagen.fill", owner=bone.id, value=0)
    values = [dict(consumer="collagen", target=bone.id)]
    tissues = [r for r in session.document.objects if isinstance(r, TissueVCP)]
    if tissues:
        target = largest(session, tissues).id
        session.command("tissue.field.create", target=target, name="benchmark", domain="REST")
        session.wait()
        values.append(
            dict(consumer="tissue_weights", target=target, name="benchmark", stage="rest")
        )
    return values


def scene(session, target):
    rows = []
    for item in (*session.document.entities, *session.document.objects):
        if item.id == target or not (
            isinstance(item, TissueVCP) or item in session.document.entities
        ):
            continue
        try:
            provider = surface_providers.get(
                session.engine, session.document, session.assets, item.id
            )
            rows.append(dict(asset=provider.asset_id, frame=provider.frame))
        except ValueError:
            pass
    return rows


def options(session, case, index):
    camera = centered_camera(session, case["target"])
    camera[-1] = index % 2
    return dict(
        case,
        view=camera,
        obstacles=scene(session, case["target"]),
        brush=[100, 0.7, 0.8, 1.3, bool(index % 3)],
        samples=[[-30, 0], [30, 10]] if index % 2 else [[x, x / 6] for x in range(-30, 31)],
    )


def centered_camera(session, target):
    value = surface_providers.get(session.engine, session.document, session.assets, target)
    center = value.resource.mesh.array(0).mean(axis=0)
    camera = list(VIEW)
    camera[:3] = session.engine.world_point(value.frame, center)
    camera[2] += 4
    return camera


def preview(session, values, new):
    if new:
        state = session.command("painting.preview", **values)
    else:
        values = dict(values)
        kind = values.pop("consumer")
        operation = "skin.inspect.paint" if kind == "collagen" else "tissue.inspect.paint"
        state = session.command(operation, **values)
    session.wait()
    return state


def candidate(session, case, state, new):
    if new:
        status = session.command("painting.status", token=state["token"])
        assert status["state"] == "ready", status
        return session.painting.values[case["consumer"]].asset["resource"]
    kind = "collagen" if case["consumer"] == "collagen" else "paint"
    value = session.tissue_inspection.values[kind]
    assert value.state == "ready", value.error
    return value.asset["resource"]


def trials(session, case, args):
    rows = []
    for index in range(12):
        values = options(session, case, index)
        start = perf_counter()
        state = preview(session, values, args.new)
        elapsed = (perf_counter() - start) * 1000
        resource = candidate(session, case, state, args.new)
        np.save(args.output / f"{case['consumer']}-{index}.npy", resource.values)
        rows.append(measurement(session, resource, elapsed))
    return rows, state


def measurement(session, resource, elapsed):
    return dict(
        ms=elapsed,
        count=len(resource.values),
        bytes=resource.bytes,
        projection_cache_bytes=session.engine.paint_surfaces.bytes,
    )


def commit(session, case, state, new):
    if new:
        session.command("painting.commit", token=state["token"])
    else:
        operation = (
            "skin.collagen.paint.commit"
            if case["consumer"] == "collagen"
            else "tissue.field.paint.commit"
        )
        session.command(operation, job=state["job"])
    session.wait()


def benchmark(session, case, args):
    rows, state = trials(session, case, args)
    before, cursor = session.document, session.history.cursor
    start = perf_counter()
    commit(session, case, state, args.new)
    elapsed = (perf_counter() - start) * 1000
    restored(session, before, cursor)
    return dict(
        case=case,
        previews=rows,
        commit_wait_ms=elapsed,
        cancel_ms=cancellations(session, case, args),
    )


def restored(session, before, cursor):
    assert session.history.cursor == cursor + 1
    session.command("undo")
    session.wait()
    assert session.document.objects == before.objects and session.document.skin == before.skin


def cancellations(session, case, args):
    values, rows = options(session, case, 3), []
    for _ in range(5):
        before, start = session.document, perf_counter()
        cancel_request(session, values, args.new)
        session.wait()
        rows.append((perf_counter() - start) * 1000)
        assert session.document is before
    return rows


def cancel_request(session, values, new):
    if new:
        state = session.command("painting.preview", **values)
        session.command("painting.cancel", token=state["token"])
    else:
        case = dict(values)
        kind = case.pop("consumer")
        operation = "skin.inspect.paint" if kind == "collagen" else "tissue.inspect.paint"
        session.command(operation, **case)
        session.command("tissue.inspect.cancel", kind="collagen" if kind == "collagen" else "paint")


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        fingerprint = load(session, args)
        values = cases(session)
        if args.profile:
            session.command("profile.start")
        before = system_times()
        results = [benchmark(session, case, args) for case in values]
        data = dict(results=results, background=system_load(before), qt_loaded=qt_loaded())
        finish(session, args, data, fingerprint)
    (args.output / "result.json").write_text(json.dumps(data, indent=2))
    print(json.dumps(data), flush=True)


def finish(session, args, data, fingerprint):
    if args.profile:
        session.command("profile.stop", path=str(args.output / "painting.afprofile.zip"), wait=True)
    assert fingerprint == digest(args.project)
    data["source_sha256"] = fingerprint


def qt_loaded():
    import sys

    return any(key.startswith("PySide6") for key in sys.modules)


if __name__ == "__main__":
    run(arguments())
