"""Trace source Blender controls and retained attachment state without saving a project."""

import json
import sys
from contextlib import contextmanager
from dataclasses import asdict
from functools import partial
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_capture import bones, edit
from shortcut_parity_blender_runtime import drain, register


def matrix(value):
    return [v for row in value for v in row]


def scalar_properties(value):
    result = {}
    for prop in value.bl_rna.properties:
        if prop.type in ("BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"):
            item = getattr(value, prop.identifier)
            result[prop.identifier] = list(item) if getattr(prop, "is_array", False) else item
        elif prop.type == "POINTER" and prop.identifier != "rna_type":
            item = getattr(value, prop.identifier)
            result[prop.identifier] = getattr(item, "name", None)
    return result


def object_data(obj):
    data = dict(name=obj.name, type=obj.type, world=matrix(obj.matrix_world))
    data.update(local=matrix(obj.matrix_local), basis=matrix(obj.matrix_basis))
    data.update(
        parent=obj.parent.name if obj.parent else "", inverse=matrix(obj.matrix_parent_inverse)
    )
    data["modifiers"] = [scalar_properties(m) for m in obj.modifiers]
    if obj.type == "CURVE":
        data["splines"] = [spline_data(s) for s in obj.data.splines]
    return data


def spline_data(spline):
    return dict(
        closed=spline.use_cyclic_u,
        points=[
            dict(co=list(p.co), left=list(p.handle_left), right=list(p.handle_right))
            for p in spline.bezier_points
        ],
    )


def snapshot(root, output, name):
    import numpy as np

    folder = output / "blender" / name
    folder.mkdir(parents=True, exist_ok=True)
    arrays = {}
    data = dict(entities=entity_records(root), geometry=bones(root, arrays))
    geometry = {s.geometry_object_ref for s in root.af_scp_system.scps}
    data["objects"] = [object_data(o) for o in bpy.context.scene.objects if relevant(o, geometry)]
    (folder / "detail.json").write_text(json.dumps(data, indent=2, default=list), encoding="utf-8")
    np.savez_compressed(folder / "geometry.npz", **arrays)


def entity_records(root):
    from anthroforge.core.scp_runtime.runtime_state import snapshot_attachment_runtime

    return [
        dict(scalar_properties(s), runtime=snapshot_attachment_runtime(s))
        for s in root.af_scp_system.scps
    ]


def relevant(obj, geometry):
    return not obj.get("af_fiber_id") and (
        obj in geometry or obj.type in ("CURVE", "EMPTY", "LATTICE")
    )


@contextmanager
def observe(output):
    from anthroforge.core.scp_runtime import attachment_wave_runtime as runtime

    records, original = [], runtime.execute_attachment_wave

    runtime.execute_attachment_wave = partial(record_wave, records, original)
    try:
        yield
    finally:
        runtime.execute_attachment_wave = original
        (output / "waves.json").write_text(json.dumps(records, indent=2, default=list))


def record_wave(records, original, request, *args):
    result = original(request, *args)
    records.extend(wave_records(request, result))
    return result


def wave_records(request, result):
    return [
        dict(
            operation=asdict(op),
            before=request.matrices[op.child_index].tolist(),
            after=result.matrices[op.child_index].tolist(),
        )
        for op in request.scp_operations
        if op.child_id in ("SCP_5", "SCP_6", "SCP_7", "SCP_17")
    ]


def prepare(addon, source, output):
    register(addon)
    bpy.ops.wm.open_mainfile(filepath=str(source / "matching_96_muscles.blend"), load_ui=False)
    root = bpy.data.objects["AF_ROOT"]
    plan = json.loads((source / "plan.json").read_text())
    assert drain()["complete"]
    snapshot(root, output, "baseline")
    print("PROBE_BASELINE", flush=True)
    return root, plan


def policy(root, output, case_name):
    from anthroforge.core.shortcuts.owner_backsolve import owner_backsolve_enabled

    shortcut = next(s for s in root.af_shortcut_system.shortcuts if s.id == case_name)
    data = dict(
        raw=shortcut.owner_backsolve,
        effective=owner_backsolve_enabled(shortcut),
        explicitly_set=shortcut.is_property_set("owner_backsolve"),
    )
    data["disabled_by_probe"] = "--disable-backsolve" in sys.argv
    if data["disabled_by_probe"]:
        shortcut.owner_backsolve = False
    (output / "policy.json").write_text(json.dumps(data, indent=2))


def run(addon, source, output, case_name):
    root, plan = prepare(addon, source, output)
    policy(root, output, case_name)
    with observe(output):
        outcome = edit(root, next(c for c in plan["cases"] if c["id"] == case_name))
    snapshot(root, output, case_name)
    print("PROBE_COMPLETE", case_name, outcome, flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :]
    run(*(Path(arg) for arg in args[:3]), args[3])
