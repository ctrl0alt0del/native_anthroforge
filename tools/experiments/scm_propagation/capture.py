"""Produce read-only baseline/edit copies and exact SCM evidence from the archived assembly."""

import json
import sys
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

import numpy as np
from fixture import OUT, TISSUE

from anthroforge.application import tissue_inspection_stages as stages
from anthroforge.application.projects import adopt, synchronize_loaded
from anthroforge.application.session import Session
from anthroforge.application.storage import read_package
from anthroforge.native import components

SOURCE = Path(
    "E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge"
)


def stage(session, key, label, name):
    mesh = stages.mesh(session, key, name)
    frame = stages.instance_frame(session, key, name)
    q = components.transformed(session.engine, mesh.array(0), frame)
    np.savez_compressed(
        OUT.parent / (label + "-" + name + ".npz"), points=q, triangles=mesh.array(3)
    )


def record(session, label):
    source = session.document.object(session.document.object(TISSUE).source)
    curves = {u.curve: session.document.object(u.curve) for u in source.curves}
    data = {key: asdict(item) for key, item in curves.items()}
    (OUT.parent / (label + "-paths.json")).write_text(json.dumps(data, indent=2))
    for key, item in curves.items():
        np.save(
            OUT.parent / (label + "-path-" + key + ".npy"),
            session.resources.paths[item.result.asset].path.array(),
        )
    for name in stages.STAGES:
        stage(session, TISSUE, label, name)
    session.command(
        "save", path=str((OUT.parent / (label + ".anthroforge")).resolve()), blocked_policy="wait"
    )


def run(source):
    OUT.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        adopt(session, *read_package(source, session.engine))
        synchronize_loaded(session)
        session.wait(240)
        driver = next(d for d in session.document.driving_shortcuts if d.label == "Ribs Top Radius")
        if abs(driver.value - 0.9829999208450317) > 1e-6:
            raise ValueError("Use the archived baseline with Ribs Top Radius approximately .983.")
        record(session, "before")
        session.command("driver.value", driver=driver.id, value=3.0)
        session.wait(240)
        record(session, "after")


if __name__ == "__main__":
    run(Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE)
