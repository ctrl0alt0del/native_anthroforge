"""Source/native local-shape inspection after representative migrated parameter edits."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from anthroforge.application.storage import read_package
from anthroforge.core.construction import Deformer, Target
from anthroforge.core.entities import IDENTITY
from anthroforge.core.shrinkwrap import Shrinkwrap
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import shrinkwrap
from anthroforge.native.mesh import GeometryEngine

CASES = ((13, "SCP_12", "ilium_geom"), (8, "SCP_8", "pubis_geom"), (12, "SCP_9", "ischium_geom"))


def distance(engine, vertices, target_vertices, triangles):
    mesh = engine.create_mesh(target_vertices, triangles.ravel(), np.arange(len(triangles) + 1) * 3)
    binding = Deformer(
        "SHRINKWRAP", "", Target("review"), shrinkwrap=Shrinkwrap(SurfaceReference("reference"))
    )
    target = SimpleNamespace(resource=SimpleNamespace(mesh=mesh), frame=IDENTITY)
    projected = shrinkwrap.deform(engine, vertices, binding, IDENTITY, target, 0)
    return np.linalg.norm(vertices - projected, axis=1)


def datasets(engine, folder, number, key, name, baseline=False):
    label = "baseline" if baseline else "edit-" + str(number)
    project = (
        folder / "compact-checkpoint.anthroforge"
        if baseline
        else folder / "compact-edits" / (label + ".anthroforge")
    )
    document, resources = read_package(project, engine)
    item = document.entity(key)
    mesh = resources.meshes[item.result.asset or item.asset].mesh
    source = np.load(folder / "blender-edits" / (label + "-" + name + ".npz"))
    return (source["local"], source["triangles"]), (mesh.array(0).copy(), mesh.array(3).copy())


def metric(engine, a, b):
    values = np.concatenate((distance(engine, a[0], *b), distance(engine, b[0], *a)))
    return dict(
        max=float(values.max()),
        p95=float(np.percentile(values, 95)),
        mean=float(values.mean()),
        diagonal=float(np.linalg.norm(np.ptp(a[0], axis=0))),
    )


def panel(axis, dataset, bounds, title, color):
    vertices, triangles = dataset
    axis.add_collection3d(
        Poly3DCollection(
            vertices[triangles], facecolor=color, edgecolor="#253040", linewidth=0.12, alpha=0.9
        )
    )
    center, extent = bounds
    for i, setter in enumerate((axis.set_xlim, axis.set_ylim, axis.set_zlim)):
        setter(center[i] - extent, center[i] + extent)
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=18, azim=-150)
    axis.set_axis_off()
    axis.set_title(title, fontsize=12)


def row(figure, index, a, b, label):
    merged = np.concatenate((a[0], b[0]))
    bounds = ((merged.max(axis=0) + merged.min(axis=0)) / 2, np.ptp(merged, axis=0).max() * 0.52)
    for offset, data, title, color in (
        (0, a, "Blender source", "#9cc4dd"),
        (1, b, "Migrated native", "#e9b170"),
    ):
        axis = figure.add_subplot(3, 2, index * 2 + offset + 1, projection="3d")
        panel(axis, data, bounds, title + " · " + label, color)


def run(folder):
    engine, report = GeometryEngine(), {}
    figure = plt.figure(figsize=(11, 14), layout="constrained")
    for index, (number, key, name) in enumerate(CASES):
        a, b = datasets(engine, folder, number, key, name)
        original = datasets(engine, folder, number, key, name, True)
        report[key] = dict(baseline=metric(engine, *original), changed=metric(engine, a, b))
        row(figure, index, a, b, name.removesuffix("_geom"))
    figure.savefig(folder / "source-native-shapes.png", dpi=130)
    (folder / "source-native-shapes.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    run(Path(sys.argv[1]))
