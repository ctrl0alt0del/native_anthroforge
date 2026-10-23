"""Match standalone authored-only VCP scope, retaining both skeletal sides."""

import hashlib
import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_runtime import authored_only, drain, register, save
from shortcut_parity_plan import write


def geometry_digest():
    result = {}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("af_muscle_mirror_proxy") or not obj.get("af_muscle_id"):
            continue
        points = np.empty((len(obj.data.vertices), 3))
        obj.data.vertices.foreach_get("co", points.ravel())
        result[obj.name] = hashlib.sha256(
            points.tobytes() + np.asarray(obj.matrix_world).tobytes()
        ).hexdigest()
    return result


def main(addon, output):
    register(addon)
    path = output / "matching_96_muscles.blend"
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    root = bpy.data.objects["AF_ROOT"]
    drain()
    before = geometry_digest()
    authored_only(root)
    drain()
    assert before == geometry_digest(), "Authored geometry changed while removing automatic mirrors"
    save(root, path)
    write(output / "authored-only.json", dict(preserved_meshes=len(before), changed=False))


if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[sys.argv.index("--") + 1 :]))
