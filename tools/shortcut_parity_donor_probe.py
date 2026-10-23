"""Check the original FDS donor independently of assembly import and ID remapping."""

import sys
from pathlib import Path

import bpy
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shortcut_parity_blender_capture import bones, edit, fiber_record, metadata, tissues
from shortcut_parity_blender_runtime import drain, register
from shortcut_parity_plan import read, write


def capture(root, rows, destination, runtime):
    arrays = {}
    records = bones(root, arrays) + tissues(root, rows, arrays)
    mapping = {
        app: (source, next(f.name for f in root.af_vcp_system.fibers if f.id == source))
        for row in rows
        for app, source in zip(row["fibers"], row["unit"]["fibers"], strict=True)
    }
    records.extend(fiber_record(root, key, identity, arrays) for key, identity in mapping.items())
    destination.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination / "geometry.npz", **arrays)
    write(destination / "state.json", metadata(root, records, runtime))


def main(addon, output, name):
    register(addon)
    plan = read(output / "plan.json")
    selected = [
        r for r in plan["records"] if r["unit"]["family"] == "flexor_digitorum_superficialis"
    ]
    rows = [dict(r, blender=r["unit"]["muscle"]) for r in selected]
    bpy.ops.wm.open_mainfile(filepath=rows[0]["unit"]["source"]["path"], load_ui=False)
    root = bpy.data.objects["AF_ROOT"]
    runtime = drain()
    if name != "baseline":
        runtime = edit(root, next(c for c in plan["cases"] if c["id"] == name))
    capture(root, rows, output / "fds-donor" / name, runtime)
    print("FDS_DONOR", name, runtime, flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :]
    main(Path(args[0]), Path(args[1]), args[2])
