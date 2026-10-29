"""Read-only production paging, capture lifetime, profile and hidden image evidence."""

import gc
import hashlib
import json
import sys
from functools import partial
from pathlib import Path
from time import perf_counter
from weakref import ref

import numpy as np
from profiler_system_load import system_load, system_times

from anthroforge.application import inspection_snapshots, projects, storage
from anthroforge.application.session import Session
from anthroforge.core.construction import Curve
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import scene


def timed(callback):
    start = perf_counter()
    value = callback()
    return value, (perf_counter() - start) * 1000


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def command(session, operation, **arguments):
    return timed(partial(session.command, operation, **arguments))


def editing_page(session, target, category, context, offset, signature):
    return command(
        session,
        "editing.inspect",
        target=target,
        category=category,
        context=context,
        offset=offset,
        limit=256,
        expected_revision=signature,
    )


def paged(session, target, category="CURVE", **context):
    offset, signature, total, samples = 0, None, 0, []
    while offset is not None:
        page, elapsed = editing_page(session, target, category, context, offset, signature)
        samples.append(elapsed)
        signature, offset = page["revision"], page["next_offset"]
        total += len(page["components"])
    assert total == page["total"]
    return dict(target=target, category=category, rows=total, page_ms=samples)


def components(session):
    curves = [o for o in session.document.objects if isinstance(o, Curve)]
    rows = [paged(session, c.id) for c in curves]
    bones = [e for e in session.document.entities if e.primitive and e.primitive.kind == "IMPORTED"]
    rows.extend(paged(session, e.id, "VERTEX") for e in bones)
    return rows


def prepare(session):
    tissue = next(
        o
        for o in session.document.objects
        if isinstance(o, TissueVCP) and "Sternocleidomastoid" in o.name
    )
    session.command("tissue.preview", target=tissue.id, changes={}, part=tissue.parts[0].id)
    session.wait(180)
    state = session.command("tissue.preview.status")
    assert state["state"] == "ready", state
    return state["token"]


def captures(session, token):
    owners, durations = [], []
    for _ in range(30):
        value, elapsed = timed(
            lambda: session.command("inspection.capture", kind="tissue_inflation", token=token)
        )
        owners.append(ref(inspection_snapshots.selected(session, value["snapshot"])))
        durations.append(elapsed)
    gc.collect()
    assert sum(owner() is not None for owner in owners) == 1
    return value["snapshot"], dict(capture_ms=durations, api_snapshots_retained=1)


def exact_pages(session, snapshot):
    owner = inspection_snapshots.selected(session, snapshot)
    rows = []
    for layer in owner.layers:
        for name in inspection_snapshots.metadata(layer)["buffers"]:
            expected = inspection_snapshots.array(layer, name)
            rows.append(buffer_pages(session, snapshot, layer.identity, name, expected))
    return rows


def buffer_pages(session, snapshot, layer, name, expected):
    offset, timings = 0, []
    options = dict(snapshot=snapshot, layer=layer, buffer=name, limit=4096)
    while offset is not None:
        page, elapsed = command(session, "inspection.geometry", offset=offset, **options)
        end = offset + len(page["values"])
        np.testing.assert_array_equal(page["values"], expected[offset:end])
        timings.append(elapsed)
        offset = page["next_offset"]
    return dict(layer=layer, buffer=name, rows=len(expected), page_ms=timings)


def camera(session, snapshot, yaw):
    value = inspection_snapshots.selected(session, snapshot)
    layers = [r for r in value.layers if r.kind == "MESH" and r.resource]
    bounds = scene.bounds(
        session.engine, [r.resource.handle for r in layers], [r.frame for r in layers]
    )
    low, high = np.array(bounds[:3]), np.array(bounds[3:])
    return [*((low + high) * 0.5).tolist(), -12, yaw, 45, float(max(high - low) * 2.5)]


def exports(session, snapshot, output, images):
    rows = []
    options = dict(snapshot=snapshot, images=images, wait=True)
    for yaw in [0, 55] if images else [0]:
        path = str((output / f"candidate-{yaw}.afinspection.zip").resolve())
        view = dict(mode="Split", camera=camera(session, snapshot, yaw))
        result, elapsed = command(session, "inspection.export", path=path, view=view, **options)
        rows.append(dict(result=result, wall_ms=elapsed))
    return rows


def record(session, path, output, images):
    (document, resources), load = timed(lambda: storage.read_package(Path(path), session.engine))
    projects.adopt(session, document, resources)
    before, cursor, load_context = session.document, session.history.cursor, system_times()
    session.command("profile.start")
    rows = dict(load_ms=load, components=components(session))
    token = prepare(session)
    snapshot, rows["ownership"] = captures(session, token)
    rows["geometry"] = exact_pages(session, snapshot)
    rows["exports"] = exports(session, snapshot, output, images)
    session.command("inspection.release", snapshot=snapshot)
    stop_profile(session, output)
    assert session.document is before and session.history.cursor == cursor
    return dict(rows, context=system_load(load_context), qt_imported="PySide6" in sys.modules)


def stop_profile(session, output):
    path = str((output / "production.afprofile.zip").resolve())
    session.command("profile.stop", path=path, wait=True)


def main(path, directory, images):
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    original, session = file_hash(path), Session()
    try:
        evidence = record(session, path, output, images)
        assert file_hash(path) == original
        evidence.update(source_sha256=original, unchanged=True)
        (output / "production.json").write_text(json.dumps(evidence, indent=2), "utf-8")
        print(json.dumps(dict(complete=True, output=str(output), qt=evidence["qt_imported"])))
    finally:
        session.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--images" in sys.argv[3:])
