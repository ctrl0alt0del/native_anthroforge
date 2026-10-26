"""Run in background Blender 5.0.1 to capture the skin proxy Smooth modifier."""

import json
import sys
from pathlib import Path

import bpy

POINTS = [(0, 0, 0), (1, 0, 0), (2, 0, 0.4), (0, 1, 0), (1, 1, 0.2), (2, 1, 0.6)]
FACES = [(0, 1, 4, 3), (1, 2, 5, 4)]


def case(points, iterations):
    obj = create(points)
    modifier = obj.modifiers.new("Smooth", "SMOOTH")
    modifier.factor, modifier.iterations = 0.42, iterations
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    output = evaluated.to_mesh()
    result = dict(
        points=points,
        faces=FACES,
        iterations=iterations,
        result=[list(v.co) for v in output.vertices],
    )
    evaluated.to_mesh_clear()
    bpy.data.objects.remove(obj, do_unlink=True)
    return result


def create(points):
    mesh = bpy.data.meshes.new("Proxy")
    mesh.from_pydata(points, [], FACES)
    obj = bpy.data.objects.new("Proxy", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def main():
    path = Path(sys.argv[sys.argv.index("--") + 1])
    cases = [case(points, steps) for points in (POINTS, [*POINTS, (3, 3, 3)]) for steps in (1, 10)]
    payload = dict(
        blender=bpy.app.version_string, source="Blender v5.0.1 MOD_smooth.cc", cases=cases
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
