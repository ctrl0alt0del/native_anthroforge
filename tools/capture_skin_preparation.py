"""Background Blender oracle for real addon Decimate, Smooth and BMesh preparation."""

import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter

import bpy
import numpy as np


def arrays(mesh):
    mesh.calc_loop_triangles()
    points = np.empty((len(mesh.vertices), 3), np.float64)
    faces = np.empty((len(mesh.loop_triangles), 3), np.int32)
    mesh.vertices.foreach_get("co", points.ravel())
    mesh.loop_triangles.foreach_get("vertices", faces.ravel())
    normals = np.empty_like(points)
    edges = np.empty((len(mesh.edges), 2), np.int32)
    mesh.vertex_normals.foreach_get("vector", normals.ravel())
    mesh.edges.foreach_get("vertices", edges.ravel())
    return dict(points=points, faces=faces, normals=normals, edges=edges)


def stage(obj, name, operation, output, timings):
    started = perf_counter()
    operation()
    timings[name] = perf_counter() - started
    output.update({name + "_" + key: value for key, value in arrays(obj.data).items()})
    print(name, timings[name], len(obj.data.polygons), flush=True)


def smooth(obj):
    modifier = obj.modifiers.new("Source Smooth", "SMOOTH")
    modifier.factor, modifier.iterations = 0.42, 10
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def prepare(source):
    mesh = bpy.data.meshes.new("Captured envelope")
    mesh.from_pydata(source["vertices"].tolist(), [], source["triangles"].tolist())
    obj = bpy.data.objects.new("Captured envelope", mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def capture(addon, source, target):
    sys.path.insert(0, str(addon.parent))
    from anthroforge.adapters.topology.engine import guides, instant

    obj, output, timings = prepare(source), {}, {}
    output.update({"input_" + key: value for key, value in arrays(obj.data).items()})
    plane = instant.SymmetryPlane(source["plane_origin"], source["plane_normal"])
    stage(obj, "decimate", lambda: guides._decimate(obj, target), output, timings)
    stage(obj, "smooth", lambda: smooth(obj), output, timings)
    stage(obj, "half", lambda: instant.bisect_left_half(obj, plane), output, timings)
    return output, timings


def main():
    addon, path, destination = map(Path, sys.argv[sys.argv.index("--") + 1 :])
    with np.load(path, allow_pickle=False) as source:
        output, timings = capture(addon, source, 64000)
    metadata = dict(
        source=str(path),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        target=64000,
        blender=bpy.app.version_string,
        build=bpy.app.build_hash.decode(),
        seconds=timings,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez(destination, **output, metadata=json.dumps(metadata))
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
