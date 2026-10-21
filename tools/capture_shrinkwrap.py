"""Blender 5.0.1 background reference; no addon and no file saves."""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

VERTICES = [(-1, -1, 0), (1, -1, 0), (1, 1, 0.3), (-1, 1, 0)]
PROBES = [(0, 0, 2), (0.2, 0.3, -2), (2, 2, 0.1), (0.1, 0.2, 0.05)]


def object_mesh(name, vertices, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def flat(matrix):
    return [float(x) for row in matrix for x in row]


def case(target, mode, offset, transformed):
    owner = object_mesh("probes", PROBES, [])
    owner.matrix_world = Matrix.Translation((0.3, -0.2, 0.7)) if transformed else Matrix.Identity(4)
    target.matrix_world = Matrix.Diagonal((1.3, 0.6, 2, 1)) if transformed else Matrix.Identity(4)
    group = owner.vertex_groups.new(name="Influence")
    for i, weight in enumerate((1, 0.5, 0, 1)):
        group.add([i], weight, "REPLACE")
    modifier = owner.modifiers.new("Wrap", "SHRINKWRAP")
    modifier.target, modifier.wrap_mode, modifier.offset = target, mode, offset
    modifier.vertex_group = group.name
    bpy.context.view_layer.update()
    result = owner.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    return record(owner, target, result, mode, offset)


def record(owner, target, result, mode, offset):
    return dict(
        mode=mode,
        offset=offset,
        owner=flat(owner.matrix_world),
        target=flat(target.matrix_world),
        points=PROBES,
        weights=[1, 0.5, 0, 1],
        expected=[list(v.co) for v in result.vertices],
    )


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    target = object_mesh("Target", VERTICES, [(0, 1, 2), (0, 2, 3)])
    modes = ("ON_SURFACE", "INSIDE", "OUTSIDE", "OUTSIDE_SURFACE")
    cases = [
        case(target, mode, offset, transformed)
        for mode in modes
        for offset in (-0.15, 0, 0.2)
        for transformed in (False, True)
    ]
    output = dict(
        blender=bpy.app.version_string, vertices=VERTICES, faces=[[0, 1, 2], [0, 2, 3]], cases=cases
    )
    Path(sys.argv[-1]).write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
