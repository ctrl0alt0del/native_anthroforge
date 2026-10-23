"""Blender-only read-only capture of local/property/world transform relationships."""

import hashlib
import json
import sys
from pathlib import Path

import bpy


def frame(value):
    return [list(row) for row in value]


def record(item):
    return dict(
        name=item.name,
        parent=item.parent.name if item.parent else "",
        world=frame(item.matrix_world),
        local=frame(item.matrix_local),
        basis=frame(item.matrix_basis),
        parent_inverse=frame(item.matrix_parent_inverse),
        location=list(item.location),
        rotation=list(item.rotation_euler),
        scale=list(item.scale),
        constraints=[(c.name, c.type, c.mute) for c in item.constraints],
    )


def main(source, output):
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    values = [record(item) for item in bpy.data.objects]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    data = dict(source=str(source), sha256=before, blender=bpy.app.version_string, objects=values)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Captured", len(values), "frames without saving the source")


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[sys.argv.index("--") + 1 :]))
