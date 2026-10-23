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


def authored_only(root):
    from anthroforge.core.visualization.vcp_mirror_runtime import sync_vcp_mirrors

    for fiber in root.af_vcp_system.fibers:
        fiber["af_authoring_symmetry"] = "explicit"
    sync_vcp_mirrors(root=root, scene=bpy.context.scene)


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


def scene_audit(root):
    objects = tuple(bpy.context.scene.objects)
    fibers = [o for o in objects if o.get("af_fiber_proxy") and not o.get("af_fiber_mirror_proxy")]
    return dict(
        source_fiber_proxies=len(fibers),
        hidden_source_fibers=sum(o.hide_get() for o in fibers),
        wire_source_fibers=sum(o.display_type == "WIRE" for o in fibers),
        mirrored_fiber_proxies=sum(bool(o.get("af_fiber_mirror_proxy")) for o in objects),
        mirrored_muscle_proxies=sum(bool(o.get("af_muscle_mirror_proxy")) for o in objects),
        scp_records=len(root.af_scp_system.scps),
        native_muscle_records=len(root.af_vcp_system.muscles),
    )
