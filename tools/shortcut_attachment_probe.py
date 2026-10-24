"""Read-only authored/control/attachment snapshots for shortcut parity diagnosis."""

import json
import sys
from contextlib import closing
from dataclasses import asdict
from pathlib import Path

import numpy as np
from qualify_retained_attachment_edits import load
from shortcut_parity_app_capture import capture, edit

from anthroforge.application.object_frames import Frames
from anthroforge.application.session import Session
from anthroforge.core.construction import Control, Curve
from anthroforge.core.fibers import Fiber


def definition(item):
    data = asdict(item)
    for key in ("result", "pose_receipt", "preview", "capture_parent_matrix"):
        data.pop(key, None)
    return data


def detail(session, output):
    frames = Frames(session.engine, session.document)
    objects = [
        o for o in session.document.registry.records.values() if isinstance(o, (Control, Curve))
    ]
    objects = [o for o in objects if not isinstance(o, Fiber)]
    data = dict(entities=[definition(e) for e in session.document.entities])
    data["construction"] = [dict(definition(o), world=frames.world(o.id)) for o in objects]
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")


def snapshot(session, output, name):
    destination = output / "app" / name
    capture(session, destination, 0)
    detail(session, destination / "detail.json")
    meshes = {}
    for entity in session.document.entities:
        if entity.attachment.material_asset:
            mesh = session.assets[entity.attachment.material_asset].mesh
            meshes[entity.id + "__material"] = mesh.array(0).copy()
            meshes[entity.id + "__material_triangles"] = mesh.array(3).copy()
    np.savez_compressed(destination / "materials.npz", **meshes)


def run(source, output, case_name):
    plan = json.loads(source.read_text())
    case = next(c for c in plan["cases"] if c["id"] == case_name)
    with closing(Session()) as session:
        load(session, Path(plan["standalone"]))
        snapshot(session, output, "baseline")
        edit(session, case)
        snapshot(session, output, case_name)
        assert not session.scheduler.errors, session.scheduler.errors
    print(case_name, "attachment/control snapshots complete")


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
