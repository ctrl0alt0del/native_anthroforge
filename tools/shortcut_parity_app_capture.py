"""Export accepted world geometry after genuine standalone shortcut operations."""

import sys
from contextlib import closing
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import numpy as np
from qualify_retained_attachment_edits import load
from shortcut_parity_plan import read, write

from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.components import transformed
from anthroforge.native.scene import entity_frame


def mesh_data(session, item, frame, arrays):
    key = item.result.asset or getattr(item, "asset", "")
    if not key:
        return dict(empty=True)
    mesh = session.assets[key].mesh
    return store_mesh(session, item.id, mesh, frame, arrays)


def store_mesh(session, key, mesh, frame, arrays):
    arrays[key + "__vertices"] = transformed(session.engine, mesh.array(0), frame)
    arrays[key + "__triangles"] = mesh.array(3).copy()
    return dict(vertices=len(mesh.array(0)), triangles=len(mesh.array(3)))


def path_data(session, item, frame, arrays):
    if not item.result.asset:
        return dict(empty=True)
    path = session.resources.paths[item.result.asset].path
    arrays[item.id + "__path"] = transformed(session.engine, path.array()[:, :3], frame)
    return dict(
        bindings=[asdict(b) for b in item.bindings], supports=[asdict(s) for s in item.supports]
    )


def record(session, item, frames, arrays):
    frame = entity_frame(session.engine, item) if isinstance(item, SCP) else frames.world(item.id)
    data = dict(id=item.id, name=item.name, kind=type(item).__name__, frame=list(frame))
    data["status"] = asdict(item.result)
    data["data"] = (
        path_data(session, item, frame, arrays)
        if isinstance(item, Fiber)
        else mesh_data(session, item, frame, arrays)
    )
    if isinstance(item, SCP):
        data.update(pose=list(item.matrix), attachment=asdict(item.attachment), parent=item.parent)
    if isinstance(item, TissueVCP):
        data.update(tissue_stages(session, item, frame, arrays))
    return data


def tissue_stages(session, item, frame, arrays):
    for label in ("base", "rest", "intrinsic"):
        result = getattr(item, label + "_result")
        if result.asset:
            store_mesh(
                session, item.id + "__" + label, session.assets[result.asset].mesh, frame, arrays
            )
    return dict(
        intrinsic_status=asdict(item.intrinsic_result), parts=[asdict(p) for p in item.parts]
    )


def capture(session, destination, elapsed):
    arrays, frames = {}, Frames(session.engine, session.document)
    items = [
        r
        for r in session.document.registry.records.values()
        if isinstance(r, (SCP, TissueVCP, Fiber))
    ]
    records = [record(session, item, frames, arrays) for item in items]
    destination.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination / "geometry.npz", **arrays)
    write(destination / "state.json", metadata(session, records, elapsed))


def metadata(session, records, elapsed):
    return dict(
        objects=records,
        seconds=elapsed,
        metres_per_coordinate=1.0,
        display_metres_per_unit=session.document.metres_per_unit,
        jobs=[
            dict(id=j.id, label=j.label, state=j.state, error=j.error)
            for j in session.scheduler.jobs
        ],
        errors=session.scheduler.errors,
    )


def edit(session, case):
    mapping = case["mapping"]
    if "driver" in mapping:
        session.command("driver.value", driver=mapping["driver"], value=case["value"])
    else:
        session.command("shortcut.set", reference=mapping["reference"], value=case["value"])
    session.wait(600)


def main(output, name):
    plan = read(output / "plan.json")
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        start = perf_counter()
        if name != "baseline":
            edit(session, next(c for c in plan["cases"] if c["id"] == name))
        capture(session, output / "app" / name, perf_counter() - start)
        print(name, "complete", session.scheduler.errors, flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]), sys.argv[2])
