"""Background Blender adapter for the real addon update pipeline."""

import sys
import time
from pathlib import Path

import bpy


def register(addon):
    sys.path.insert(0, str(Path(addon).parent))
    import anthroforge

    if not hasattr(bpy.types.Object, "af_scp_system"):
        anthroforge.register()


def drain(timeout=600):
    from anthroforge.core.visualization import fiber_refinement, sync_runner

    deadline, quiet = time.monotonic() + timeout, 0
    while time.monotonic() < deadline and quiet < 3:
        bpy.context.view_layer.update()
        pending = sync_runner._PENDING
        for item in pending:
            item.due_at = 0
        if pending:
            sync_runner._flush_pending(retry_failed=False)
        fiber_refinement.drain_fiber_refinements()
        quiet = quiet + 1 if not pending and not fiber_refinement._QUEUE else 0
    return dict(complete=quiet >= 3, pending=len(sync_runner._PENDING), passes=quiet)


def save(root, path):
    from anthroforge.adapters.authoring.scene import StaticScene

    StaticScene(root, bpy.context.scene).save_debug_copy(str(path))


def clear_construction(root):
    from anthroforge.core.vcp.prop_update_guard import suppress_vcp_prop_updates

    tags = ("af_fiber_id", "af_fiber_surface_id", "af_muscle_id")
    doomed = [o for o in bpy.data.objects if any(o.get(t) for t in tags)]
    with suppress_vcp_prop_updates():
        for name in ("muscles", "fiber_surfaces", "fibers", "authored_points"):
            getattr(root.af_vcp_system, name).clear()
    for obj in doomed:
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.context.view_layer.update()
    drain()


def muscle_objects(root, key, role="INFL"):
    return [
        o
        for o in bpy.context.scene.objects
        if o.get("af_root_name") == root.name
        and o.get("af_muscle_id") == key
        and o.get("af_muscle_surface") == role
        and not o.name.endswith("_MIR")
    ]
