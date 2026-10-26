"""Blender background qualification: canonical triangle inputs used by skin generation."""

import json
import sys
from pathlib import Path

import bpy


def arrays(mesh):
    mesh.calc_loop_triangles()
    return dict(
        points=[list(vertex.co) for vertex in mesh.vertices],
        faces=[list(face.vertices) for face in mesh.loop_triangles],
        edges=[list(edge.vertices) for edge in mesh.edges],
    )


def case(row):
    mesh = bpy.data.meshes.new(row["name"])
    mesh.from_pydata(row["points"], [], row["faces"])
    mesh.update()
    source = arrays(mesh)
    obj = bpy.data.objects.new(row["name"], mesh)
    bpy.context.scene.collection.objects.link(obj)
    modifier = obj.modifiers.new("Decimate", "DECIMATE")
    modifier.ratio = max(0.01, min(1.0, row["target"] / len(mesh.polygons)))
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    result = arrays(evaluated.to_mesh())
    evaluated.to_mesh_clear()
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    return dict(name=row["name"], source=source, result=result, target=row["target"])


def small_cases():
    tetra = dict(
        name="tetrahedron",
        points=[[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]],
        faces=[[0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]],
        target=1,
    )
    nonmanifold = dict(
        name="small_nonmanifold",
        target=1,
        points=[[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1]],
        faces=[[0, 1, 2], [1, 0, 3], [0, 1, 4]],
    )
    return [tetra, nonmanifold]


def main():
    source, destination = map(Path, sys.argv[sys.argv.index("--") + 1 :])
    rows = json.loads(source.read_text())["cases"] + small_cases()
    report = dict(
        source=f"Blender {bpy.app.version_string} {bpy.app.build_hash.decode()}",
        construction="Mesh.from_pydata triangles, calculate edges, Decimate collapse defaults",
        cases=[case(row) for row in rows],
    )
    destination.write_text(json.dumps(report, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
