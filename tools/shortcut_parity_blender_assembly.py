"""Compose exactly the migration donors into a separate native addon assembly."""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_runtime import authored_only, clear_construction, drain, register, save
from shortcut_parity_plan import read, write


def import_group(root, group):
    from anthroforge.core.importing.model import PackageSnapshot
    from anthroforge.core.importing.vcp import apply_vcp_snapshot

    package = PackageSnapshot.from_dict(read(group["package"]))
    before = {m.id for m in root.af_vcp_system.muscles}
    result = apply_vcp_snapshot(package, root, bpy.context)
    added = [m for m in root.af_vcp_system.muscles if m.id not in before]
    assert len(added) == len(package.muscles), result.warnings
    mapping = {s.source_id: d.id for s, d in zip(package.muscles, added, strict=True)}
    print("IMPORTED", len(added), result.warnings, flush=True)
    return mapping, result.warnings


def assemble(root, plan, output):
    rows, warnings = [], []
    for index, group in enumerate(plan["groups"]):
        mapping, issues = import_group(root, group)
        warnings.extend(issues)
        rows.extend(dict(r, blender=mapping[r["unit"]["muscle"]]) for r in group["records"])
        write(
            output / "assembly-progress.json", dict(groups=index + 1, rows=rows, warnings=warnings)
        )
    return rows, warnings


def main(addon, source, output):
    register(addon)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    root = bpy.data.objects["AF_ROOT"]
    clear_construction(root)
    plan = read(output / "plan.json")
    rows, warnings = assemble(root, plan, output)
    authored_only(root)
    state = drain()
    write(output / "blender-assembly.json", dict(rows=rows, warnings=warnings, runtime=state))
    assert state["complete"], state
    save(root, output / "matching_96_muscles.blend")


if __name__ == "__main__":
    main(*(Path(p) for p in sys.argv[sys.argv.index("--") + 1 :]))
