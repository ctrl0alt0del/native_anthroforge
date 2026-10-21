"""Blender 5.0.1 background-only compact Simple/displacement reference capture."""

import json
import sys
from pathlib import Path

import bpy


def capture(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    data = dict(
        vertices=[list(v.co) for v in mesh.vertices],
        faces=[list(f.vertices) for f in mesh.polygons],
    )
    evaluated.to_mesh_clear()
    return data


def plate():
    mesh = bpy.data.meshes.new("Plate")
    mesh.from_pydata(
        [(0, 0, 0), (2, 0, 0.2), (3, 0, 0.7), (0, 1, 0.4), (2, 1, 0.8), (3, 1, 1.2)],
        [],
        [(0, 1, 4, 3), (1, 2, 5, 4)],
    )
    obj = bpy.data.objects.new("Plate", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obj = plate()
    source = capture(obj)
    mod = obj.modifiers.new("Simple", "SUBSURF")
    mod.subdivision_type, mod.levels = "SIMPLE", 2
    bpy.context.view_layer.update()
    output = dict(blender=bpy.app.version_string, source=source, subdivided=capture(obj))
    Path(sys.argv[-1]).write_text(json.dumps(output, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
