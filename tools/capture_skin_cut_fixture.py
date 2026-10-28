"""Capture addon guide-hole selection using the maintained annulus fixture."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np


def anchor_object(annuli, expected):
    patch = annuli.AnnulusPatch(
        "fixture",
        ("0", "1"),
        np.array(expected["points"]),
        np.array(expected["normals"]),
        np.array(expected["faces"]),
    )
    return annuli.create_patch_object(patch, bpy.context.scene.collection, None)


def cut(annuli, instant, row, centered):
    anchor = anchor_object(annuli, row["chosen"])
    plane = instant.SymmetryPlane(np.zeros(3), np.array([1, 0, 0])) if centered else None
    faces = np.array(row["faces"])
    result = instant.cut_guide_holes(np.array(row["vertices"]), faces, [anchor], plane)
    retained = {tuple(face) for face in result}
    bpy.data.objects.remove(anchor, do_unlink=True)
    return [i for i, face in enumerate(faces) if tuple(face) in retained]


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    annuli = importlib.import_module("adapters.topology.engine.annuli")
    instant = importlib.import_module("adapters.topology.engine.instant")
    rows = json.loads(Path(args[1]).read_text(encoding="utf-8"))["cases"]
    cases = [
        dict(case=i, centered=flag, kept=cut(annuli, instant, row, flag))
        for i, row in enumerate(rows)
        for flag in (False, True)
    ]
    Path(args[2]).write_text(json.dumps(cases, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
