"""Read-only Blender extraction of evaluated skull colliders and saved fiber paths."""

import hashlib
import json
import sys
from pathlib import Path

import bpy

MESHES = ("Cranium", "brow_ridge_geom", "mandible_front_geom", "mandible_side_geom")
FIBERS = ("AF_FIBER_1", "AF_FIBER_2", "AF_FIBER_9", "AF_FIBER_13")


def geometry(name, depsgraph):
    source = bpy.data.objects[name].evaluated_get(depsgraph)
    mesh = source.to_mesh()
    try:
        mesh.calc_loop_triangles()
        return dict(
            name=name,
            vertices=[list(source.matrix_world @ vertex.co) for vertex in mesh.vertices],
            triangles=[list(triangle.vertices) for triangle in mesh.loop_triangles],
        )
    finally:
        source.to_mesh_clear()


def fiber(name):
    source = bpy.data.objects[name]
    points = json.loads(source["af_fiber_points_world"])
    return dict(name=name, saved_path=points, closed=source.data.splines[0].use_cyclic_u)


def run(output):
    source = Path(bpy.data.filepath)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    payload = dict(
        source=str(source),
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        blender=bpy.app.version_string,
        build=bpy.app.build_hash.decode(),
        colliders=[geometry(name, depsgraph) for name in MESHES],
        fibers=[fiber(name) for name in FIBERS],
    )
    output.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    report(output, payload)


def report(output, payload):
    print(
        json.dumps(
            dict(output=str(output), vertices=[len(c["vertices"]) for c in payload["colliders"]])
        )
    )


if __name__ == "__main__":
    run(Path(sys.argv[sys.argv.index("--") + 1]))
