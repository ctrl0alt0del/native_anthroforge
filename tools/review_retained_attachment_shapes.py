"""Offscreen inspection of saved FDS crop and Thumb attachment shapes; no project edits."""

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from anthroforge.application.object_frames import Frames
from anthroforge.application.storage import read_package
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.components import transformed
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.scene import entity_frame

FDS = "Flexor digitorum superficialis.L"
THUMB = (
    "Extensor pollicis brevis.L",
    "Abductor pollicis brevis.L",
    "Flexor pollicis brevis superficial.L",
)


def included(item, number):
    if isinstance(item, SCP):
        return number == 21 and item.id == "SCP_17"
    names = THUMB if number == 21 else (FDS,)
    return isinstance(item, (Fiber, TissueVCP)) and item.name.startswith(names)


def scene(engine, path, number):
    document, resources = read_package(path, engine)
    frames, rows = Frames(engine, document), []
    for item in document.registry.records.values():
        if included(item, number):
            rows.append(geometry(engine, frames, resources, item))
    return rows


def geometry(engine, frames, resources, item):
    frame = entity_frame(engine, item) if isinstance(item, SCP) else frames.world(item.id)
    if isinstance(item, Fiber):
        points = transformed(engine, resources.paths[item.result.asset].path.array()[:, :3], frame)
        return "curve", points, None, item.name
    mesh = resources.meshes[item.result.asset or item.asset].mesh
    points = transformed(engine, mesh.array(0), frame)
    return "bone" if isinstance(item, SCP) else "tissue", points, mesh.array(3).copy(), item.name


def draw(axis, rows):
    for kind, points, triangles, _name in rows:
        if kind == "curve":
            axis.plot(*points.T, color="#007c98", linewidth=0.7)
            axis.scatter(*points[[0, -1]].T, color="#cf203d", s=8)
        else:
            color, alpha = ("#c6bc99", 0.8) if kind == "bone" else ("#dc9376", 0.38)
            axis.add_collection3d(Poly3DCollection(points[triangles], facecolor=color, alpha=alpha))


def panel(axis, rows, bounds, title, angle):
    draw(axis, rows)
    center, extent = bounds
    for i, setter in enumerate((axis.set_xlim, axis.set_ylim, axis.set_zlim)):
        setter(center[i] - extent, center[i] + extent)
    axis.set_box_aspect((1, 1, 1))
    axis.view_init(elev=angle[0], azim=angle[1])
    axis.set_axis_off()
    axis.set_title(title)


def comparison(before, after):
    all_points = np.concatenate([row[1] for row in (*before, *after)])
    bounds = ((all_points.max(0) + all_points.min(0)) / 2, np.ptp(all_points, axis=0).max() * 0.52)
    figure = plt.figure(figsize=(12, 10), layout="constrained")
    for i, angle in enumerate(((20, -35), (15, 55))):
        for j, (rows, label) in enumerate(
            ((before, "Original"), (after, "+5% — retained attachments"))
        ):
            panel(
                figure.add_subplot(2, 2, 2 * i + j + 1, projection="3d"), rows, bounds, label, angle
            )
    return figure


def review(engine, source, folder, number):
    before = scene(engine, source, number)
    after = scene(engine, folder / f"edit-{number}.anthroforge", number)
    figure = comparison(before, after)
    label = {
        15: "Humerus length / FDS",
        16: "Radius length / FDS",
        21: "Thumb thickness / seven Fibers",
    }[number]
    figure.suptitle(label + " · saved native surfaces and paths · red endpoints")
    figure.savefig(folder / f"shapes-{number}.png", dpi=130)
    plt.close(figure)


def run(source, folder):
    engine = GeometryEngine()
    for number in (15, 16, 21):
        review(engine, source, folder, number)
        print(f"Saved shape review {number}", flush=True)


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:3]))
