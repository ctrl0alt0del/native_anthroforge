"""Run with background Blender: capture the addon's ordinary armature channels and playback."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import bpy
import numpy as np


def module(path):
    spec = importlib.util.spec_from_file_location("source_fit_rig", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def mesh(data):
    geometry = bpy.data.meshes.new("Source skin")
    geometry.from_pydata(data["vertices"], [], data["quads"])
    obj = bpy.data.objects.new("Source skin", geometry)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def evaluate(obj, rig, value):
    rig["shortcut_value"] = float(value)
    rig.update_tag()
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    geometry = evaluated.to_mesh()
    output = np.empty((len(geometry.vertices), 3))
    geometry.vertices.foreach_get("co", output.ravel())
    evaluated.to_mesh_clear()
    return output.tolist()


def capture(rig, data):
    source = mesh(data)
    samples = SimpleNamespace(vertices=np.array(data["vertices"]))
    weights, matrices = np.array(data["weights"]), np.array(data["prediction"]["matrices"])
    obj, arm = rig.create(source, samples, weights)
    rig.controls(arm, data["values"], matrices, "Fixture shortcut")
    values = np.linspace(-0.2, 1.2, 15)
    return dict(
        bases=[list(map(list, bone.matrix_local)) for bone in arm.data.bones],
        channels=rig.channels(arm, matrices).tolist(),
        values=values.tolist(),
        positions=[evaluate(obj, arm, value) for value in values],
    )


def main():
    addon, fixture, output = map(Path, sys.argv[sys.argv.index("--") + 1 :])
    path = addon / "adapters/bone_fitting/rig.py"
    rig, data = module(path), json.loads(fixture.read_text())
    result = dict(
        provenance=dict(
            source=str(path),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            blender=bpy.app.version_string,
        ),
        cases={name: capture(rig, case) for name, case in data["cases"].items()},
    )
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


main()
