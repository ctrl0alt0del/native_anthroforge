"""Capture native addon shortcut outcomes in evaluated world coordinates."""

import sys
from pathlib import Path
from time import perf_counter

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_runtime import drain, muscle_objects, register, scene_audit
from shortcut_parity_plan import read, write


def mesh_data(obj, key, arrays):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = np.empty((len(mesh.vertices), 3))
        mesh.vertices.foreach_get("co", points.ravel())
        matrix = np.asarray(evaluated.matrix_world)
        arrays[key + "__vertices"] = points @ matrix[:3, :3].T + matrix[:3, 3]
        arrays[key + "__triangles"] = np.asarray([tuple(t.vertices) for t in mesh.loop_triangles])
        return dict(vertices=len(points), triangles=len(mesh.loop_triangles))
    finally:
        evaluated.to_mesh_clear()


def mesh_record(obj, key, name, kind, arrays):
    if obj is None:
        return dict(id=key, name=name, kind=kind, missing=True)
    return dict(
        id=key,
        name=name,
        kind=kind,
        blender_object=obj.name,
        frame=[v for row in obj.matrix_world for v in row],
        data=mesh_data(obj, key, arrays),
        diagnostics={
            k: str(obj[k]) for k in obj.keys() if any(s in k for s in ("error", "status", "stale"))
        },
    )


def bones(root, arrays):
    records = []
    for scp in root.af_scp_system.scps:
        if scp.geometry_object_ref:
            records.append(mesh_record(scp.geometry_object_ref, scp.id, scp.name, "SCP", arrays))
        else:
            records.append(dict(id=scp.id, name=scp.name, kind="SCP", empty=True))
    for obj in bpy.context.scene.objects:
        if obj.get("af_scp_mirror") and obj.get("af_scp_geometry"):
            key = obj["af_source_scp_id"] + "_mirror"
            records.append(mesh_record(obj, key, obj.name, "SCP", arrays))
    return records


def tissues(root, rows, arrays):
    records = []
    for row in rows:
        objects = muscle_objects(root, row["blender"])
        assert len(objects) <= 1, (row["blender"], [o.name for o in objects])
        obj = objects[0] if objects else None
        record = mesh_record(obj, row["tissue"], row["unit"]["source_name"], "TissueVCP", arrays)
        record.update(tissue_settings(root, row, arrays))
        records.append(record)
    return records


def tissue_settings(root, row, arrays):
    from anthroforge.core.importing.rna import scalar_dict

    base = muscle_objects(root, row["blender"], "BASE")
    if base:
        mesh_data(base[0], row["tissue"] + "__base", arrays)
    muscle = next(m for m in root.af_vcp_system.muscles if m.id == row["blender"])
    return dict(settings=scalar_dict(muscle))


def fiber_map(plan):
    result, index = {}, 0
    for group in plan["groups"]:
        source = read(group["package"])["fibers"]
        mapping = {
            row["source_id"]: (f"FIBER_{index + i + 1}", row["name"])
            for i, row in enumerate(source)
        }
        for record in group["records"]:
            for app, original in zip(record["fibers"], record["unit"]["fibers"], strict=True):
                result[app] = mapping[original]
        index += len(source)
    return result


def fiber_record(root, key, identity, arrays):
    from anthroforge.core.visualization.fiber_sync_helpers import persisted_fiber_points

    fiber = next(f for f in root.af_vcp_system.fibers if f.id == identity[0])
    assert fiber.name == identity[1], (fiber.name, identity)
    points = persisted_fiber_points(bpy.context.scene, root.name, fiber.id)
    if points:
        arrays[key + "__path"] = np.asarray([tuple(p) for p in points])
    return fiber_metadata(fiber, key, bool(points))


def fiber_metadata(fiber, key, present):
    from anthroforge.core.vcp.runtime_state import fiber_invalid_reason, fiber_recompute_status

    return dict(
        id=key,
        name=fiber.name,
        kind="Fiber",
        source=fiber.id,
        missing=not present,
        status=fiber_recompute_status(fiber),
        error=fiber_invalid_reason(fiber),
    )


def capture(root, plan, rows, destination, runtime):
    destination.mkdir(parents=True, exist_ok=True)
    arrays = {}
    records = bones(root, arrays) + tissues(root, rows, arrays)
    records.extend(fiber_record(root, k, v, arrays) for k, v in fiber_map(plan).items())
    np.savez_compressed(destination / "geometry.npz", **arrays)
    write(destination / "state.json", metadata(root, records, runtime))


def metadata(root, records, runtime):
    from anthroforge.core.units import unit_contract_payload

    return dict(
        objects=records,
        runtime=runtime,
        scene_scale=bpy.context.scene.unit_settings.scale_length,
        unit_contract=unit_contract_payload(root),
        blender=bpy.app.version_string,
        scene_audit=scene_audit(root),
    )


def edit(root, case):
    from anthroforge.app.use_cases.shortcut_edit import set_shortcut_value

    shortcut = next(s for s in root.af_shortcut_system.shortcuts if s.id == case["id"])
    before = value(root, shortcut)
    start = perf_counter()
    assert set_shortcut_value(bpy.context, shortcut, case["value"]), case
    runtime = drain()
    runtime.update(
        before=before,
        requested=case["value"],
        actual=value(root, shortcut),
        seconds=perf_counter() - start,
    )
    return runtime


def value(root, shortcut):
    from anthroforge.core.shortcuts import resolve_shortcut, target_value

    return float(target_value(resolve_shortcut(root, bpy.context, shortcut.data_path)))


def main(addon, output, name):
    register(addon)
    bpy.ops.wm.open_mainfile(filepath=str(output / "matching_96_muscles.blend"), load_ui=False)
    root, plan = bpy.data.objects["AF_ROOT"], read(output / "plan.json")
    runtime = drain()
    if name != "baseline":
        runtime = edit(
            root, next(c for c in plan["cases"] if c["id"] == name.removesuffix("-refresh"))
        )
    if name.endswith("-refresh"):
        runtime["explicit_refresh"] = refresh(root)
    rows = read(output / "blender-assembly.json")["rows"]
    capture(root, plan, rows, output / "blender" / name, runtime)
    print("CAPTURED", name, runtime, flush=True)


def refresh(root):
    from anthroforge.app.runtime_api import sync_scene
    from anthroforge.core.deps.dirty_hints import DirtyHints

    hints = DirtyHints(full=False)
    hints["FIBER"] = {f.id for f in root.af_vcp_system.fibers}
    sync_scene(root=root, scene=bpy.context.scene, dirty_hints=hints, source="manual")
    return drain()


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :]
    main(Path(args[0]), Path(args[1]), args[2])
