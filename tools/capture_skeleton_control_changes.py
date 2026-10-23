"""Read-only Blender geometry references for migrated radius, angle and shrink controls."""

import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from capture_shortcut_parity import register

TARGETS = ("ribs_geom", "pubis_geom", "ischium_geom", "ilium_geom")


def capture(folder, label):
    graph = bpy.context.evaluated_depsgraph_get()
    for name in TARGETS:
        item = bpy.data.objects[name].evaluated_get(graph)
        mesh = item.to_mesh()
        try:
            mesh.calc_loop_triangles()
            vertices = np.asarray([list(item.matrix_world @ v.co) for v in mesh.vertices])
            triangles = np.asarray([tuple(t.vertices) for t in mesh.loop_triangles])
            np.savez(folder / (label + "-" + name + ".npz"), vertices=vertices, triangles=triangles)
        finally:
            item.to_mesh_clear()


def assign(row, value):
    target = row["resolved"]
    obj = bpy.data.objects[target["id"]["id"]]
    if target["path"].startswith("["):
        obj[json.loads(target["path"])[0]] = value
    else:
        obj.rotation_euler[target["index"]] = value
    obj.update_tag()
    bpy.context.view_layer.update()


def run(addon, source, folder):
    register(addon)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    definitions = json.loads((folder / "donor-definitions.json").read_text())
    rows = {r["id"]: r for r in definitions["roots"]["AF_ROOT"]["shortcuts"]}
    output = folder / "blender-edits"
    output.mkdir(exist_ok=True)
    capture(output, "baseline")
    capture_changes(rows, output)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    print("Source geometry changes captured; source file unchanged.")


def capture_changes(rows, output):
    for number in (1, 8, 11, 12, 13, 14):
        row = rows["SHORTCUT_" + str(number)]
        initial = row["resolved"]["captured"]["value"]
        value = initial + 0.05 if number in (12, 13, 14) else initial * 1.05
        assign(row, value)
        capture(output, "edit-" + str(number))
        assign(row, initial)


if __name__ == "__main__":
    run(*(Path(p) for p in sys.argv[sys.argv.index("--") + 1 :]))
