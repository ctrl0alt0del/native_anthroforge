"""Extract compact owned-node references without saving or running the addon."""

import hashlib
import json
import sys
from pathlib import Path

import bpy


def parameter_values(modifier):
    return {
        item.name: modifier.get(item.identifier, getattr(item, "default_value", None))
        for item in modifier.node_group.interface.items_tree
        if item.item_type == "SOCKET"
        and item.in_out == "INPUT"
        and item.socket_type == "NodeSocketFloat"
    }


def mesh_record(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = dict(
        vertices=[list(v.co) for v in mesh.vertices],
        faces=[list(p.vertices) for p in mesh.polygons],
    )
    evaluated.to_mesh_clear()
    return result


def capture(obj, modifier):
    settings = parameter_values(modifier)
    for item in obj.modifiers:
        item.show_viewport = item == modifier
    bpy.context.view_layer.update()
    profile = next(n for n in modifier.node_group.nodes if n.type == "CURVE_FLOAT").mapping
    return dict(
        name=obj.name,
        parameters=settings,
        mesh=mesh_record(obj),
        profile=[list(p.location) for p in profile.curves[0].points],
    )


def all_cases():
    return [
        capture(obj, mod)
        for obj in bpy.data.objects
        for mod in obj.modifiers
        if mod.type == "NODES" and mod.node_group and mod.node_group.name.startswith("FingerNodes")
    ]


def main():
    source, output = map(Path, sys.argv[-2:])
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    record = dict(
        source=str(source),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        blender=bpy.app.version_string,
        cases=all_cases(),
    )
    output.write_text(json.dumps(record, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
