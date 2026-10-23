"""Reopen the comparison copy and record saved native presentation without changing it."""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_runtime import register, scene_audit
from shortcut_parity_plan import write


def presentation():
    return [
        dict(screen=screen.name, type=space.shading.type, color=space.shading.color_type)
        for screen in bpy.data.screens
        for area in screen.areas
        for space in area.spaces
        if space.type == "VIEW_3D"
    ]


def main(addon, output):
    register(addon)
    bpy.ops.wm.open_mainfile(filepath=str(output / "matching_96_muscles.blend"), load_ui=True)
    audit = scene_audit(bpy.data.objects["AF_ROOT"])
    audit["viewports"] = presentation()
    fibers = [o for o in bpy.context.scene.objects if o.get("af_fiber_proxy")]
    audit["invisible_source_fibers"] = sum(not o.visible_get() for o in fibers)
    bones = [o for o in bpy.context.scene.objects if o.get("af_scp_geometry")]
    audit["bone_colors"] = sorted({tuple(o.color) for o in bones})
    write(output / "reopened-presentation.json", audit)
    print(audit, flush=True)


if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[sys.argv.index("--") + 1 :]))
