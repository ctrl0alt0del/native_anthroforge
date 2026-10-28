"""Run in Blender 5.0.1 background mode; capture compact default-collapse controls."""

import json
import math
import sys
from pathlib import Path

import bmesh
import bpy


def sphere(name, scale):
    mesh = bpy.data.meshes.new(name)
    working = bmesh.new()
    bmesh.ops.create_icosphere(working, subdivisions=4, radius=1)
    for vertex in working.verts:
        for axis in range(3):
            vertex.co[axis] *= scale[axis]
    working.to_mesh(mesh)
    working.free()
    mesh.update()
    return mesh


def patch():
    count = 24
    points = [
        (x / count, y / count, 0.05 * math.sin(x * 0.4) * math.cos(y * 0.3))
        for y in range(count + 1)
        for x in range(count + 1)
    ]
    faces = []
    for y in range(count):
        for x in range(count):
            a = y * (count + 1) + x
            faces.extend(((a, a + 1, a + count + 2), (a, a + count + 2, a + count + 1)))
    return create_mesh(points, faces)


def create_mesh(points, faces):
    mesh = bpy.data.meshes.new("patch")
    mesh.from_pydata(points, [], faces)
    mesh.update()
    return mesh


def arrays(mesh):
    mesh.calc_loop_triangles()
    return [list(v.co) for v in mesh.vertices], [list(f.vertices) for f in mesh.loop_triangles]


def case(name, mesh, tolerance):
    points, faces = arrays(mesh)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    modifier = obj.modifiers.new("Decimate", "DECIMATE")
    modifier.ratio = 0.25
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    result_points, result_faces = arrays(evaluated.to_mesh())
    evaluated.to_mesh_clear()
    bpy.data.objects.remove(obj, do_unlink=True)
    return record(name, points, faces, result_points, result_faces, tolerance)


def record(name, points, faces, result_points, result_faces, tolerance):
    return dict(
        name=name,
        points=points,
        faces=faces,
        result_points=result_points,
        result_faces=result_faces,
        target=len(faces) // 4,
        tolerance=tolerance,
    )


def main():
    cases = [
        case("sphere", sphere("sphere", (1, 1, 1)), 0.007),
        case("ellipsoid", sphere("ellipsoid", (0.4, 0.7, 1.8)), 0.004),
        case("patch", patch(), 1e-6),
    ]
    payload = dict(
        source=f"Blender {bpy.app.version_string} {bpy.app.build_hash.decode()}",
        operation="DECIMATE collapse, ratio 0.25, all defaults",
        cases=cases,
    )
    path = Path(sys.argv[sys.argv.index("--") + 1])
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
