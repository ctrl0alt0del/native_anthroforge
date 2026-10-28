"""Render unchanged triangle arrays with identical orthographic cameras in background Blender."""

import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


def material(name, color):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (*color, 1)
    return result


def mesh_object(data):
    vertices = np.asarray(data["vertices"], dtype=np.float32)
    faces = np.asarray(data["faces" if "faces" in data else "triangles"], dtype=np.int32)
    mesh = bpy.data.meshes.new("Exact accepted triangles")
    mesh.vertices.add(len(vertices))
    mesh.vertices.foreach_set("co", vertices.ravel())
    mesh.loops.add(faces.size)
    mesh.loops.foreach_set("vertex_index", faces.ravel())
    mesh.polygons.add(len(faces))
    mesh.polygons.foreach_set("loop_start", np.arange(0, faces.size, 3, dtype=np.int32))
    mesh.polygons.foreach_set("loop_total", np.full(len(faces), 3, dtype=np.int32))
    mesh.update()
    obj = bpy.data.objects.new("Accepted geometry", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def appearance(obj, data):
    obj.data.materials.append(material("Skin", (0.55, 0.67, 0.72)))
    if "skeletal" not in data:
        return
    obj.data.materials.clear()
    obj.data.materials.append(material("Tissue", (0.55, 0.23, 0.21)))
    obj.data.materials.append(material("Bone", (0.76, 0.70, 0.56)))
    obj.data.polygons.foreach_set("material_index", np.asarray(data["skeletal"], dtype=np.int32))


def rendering(scene):
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = 1000, 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (0.035, 0.045, 0.055)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "BOTH"
    scene.display.render_aa = "16"
    scene.view_settings.view_transform = "Standard"


def camera(scene, bounds):
    data = bpy.data.cameras.new("Matched orthographic camera")
    data.type, data.ortho_scale = "ORTHO", float(np.ptp(bounds, axis=0).max()) * 1.27
    data.clip_end = 10000
    obj = bpy.data.objects.new("Camera", data)
    scene.collection.objects.link(obj)
    scene.camera = obj
    return obj, Vector(bounds.mean(0)), data.ortho_scale * 3


def views():
    return dict(
        front=(-1, 0, 0),
        back=(1, 0, 0),
        left=(0, -1, 0),
        right=(0, 1, 0),
        oblique=(-1, -1, 0.4),
    )


def capture(scene, control, output):
    obj, center, distance = control
    for name, direction in views().items():
        obj.location = center + Vector(direction).normalized() * distance
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = str(output.with_name(output.name + "-" + name + ".png"))
        bpy.ops.render.render(write_still=True)


def main():
    source, inputs, output = [Path(p).resolve() for p in sys.argv[sys.argv.index("--") + 1 :]]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("Background")
    with np.load(inputs) as reference:
        points = reference["vertices"]
        bounds = np.array([points.min(0), points.max(0)])
    with np.load(source) as data:
        appearance(mesh_object(data), data)
    rendering(scene)
    output.parent.mkdir(parents=True, exist_ok=True)
    capture(scene, camera(scene, bounds), output)


if __name__ == "__main__":
    main()
