"""Run the addon's production stitch/weld/orientation on captured common inputs."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np


def anchor(annuli, row, index):
    start, count, face, size = row["patches"][index][:4]
    samples = np.array(row["patch_samples"])[start : start + count * 5]
    faces = np.array(row["patch_faces"])[face : face + size] - start
    patch = annuli.AnnulusPatch(
        f"annulus_{index}",
        (str(index),),
        samples[:, :3].reshape(5, count, 3),
        samples[:, 3:].reshape(5, count, 3),
        faces,
    )
    return annuli.create_patch_object(patch, bpy.context.scene.collection, None)


def output(solver, row, anchors, plane):
    args = np.array(row["vertices"]), np.array(row["faces"]), anchors, plane
    result = solver._assemble(*args, row.get("allow_unstitched", False))
    return dict(
        points=result[0].tolist(),
        faces=result[1].tolist(),
        regions=result[2].tolist(),
        guides=result[3].tolist(),
        diagnostics=result[4],
    )


def capture(annuli, solver, row):
    anchors = [anchor(annuli, row, index) for index in range(len(row["patches"]))]
    value = row["plane"]
    plane = (
        None if value is None else annuli.SymmetryPlane(np.array(value[:3]), np.array(value[3:]))
    )
    try:
        row["expected"] = output(solver, row, anchors, plane)
    except (ValueError, RuntimeError) as error:
        row["error"] = str(error)
    for obj in anchors:
        bpy.data.objects.remove(obj, do_unlink=True)
    return row


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    annuli = importlib.import_module("adapters.topology.engine.annuli")
    solver = importlib.import_module("adapters.topology.solver")
    rows = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    data = dict(
        blender=bpy.app.version_string, cases=[capture(annuli, solver, row) for row in rows]
    )
    Path(args[2]).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    for row in data["cases"]:
        print(row["name"], row["error"] if "error" in row else len(row["expected"]["faces"]))


if __name__ == "__main__":
    main()
