"""Consistent-camera plots of actual native path and tissue outputs."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

P = Path("build/scm-ribs-distortion/comparison")
DATA = Path("build/scm-ribs-distortion")
LABELS = [
    "Before edit",
    "Current propagation",
    "Experimental propagation",
    "ROUTED — endpoints only",
]
TAGS = ["before", "current", "improved", "routed_endpoints"]


def geometry(tag, stage):
    file = (
        DATA / ("before-" + stage + ".npz") if tag == "before" else P / (tag + "-" + stage + ".npz")
    )
    data = np.load(file)
    return data["points"], data["triangles"]


def setup(ax, title, azimuth):
    ax.set(xlim=(-2.5, 0.6), ylim=(-3.8, 0.2), zlim=(3.0, 6.8), title=title)
    ax.set_box_aspect((3.1, 4, 3.8))
    ax.view_init(elev=15, azim=azimuth)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.tick_params(labelsize=7)


def panel(ax, tag, stage, title, azimuth, context):
    q, t = geometry(tag, stage)
    mesh = Poly3DCollection(
        q[t], facecolor="#b96f68", edgecolor="#513d3d", linewidth=0.1, alpha=0.9
    )
    ax.add_collection3d(mesh)
    if context:
        bones(ax, "before" if tag == "before" else "after")
    setup(ax, title, azimuth)


def surfaces(stage, azimuth, context=False):
    fig = plt.figure(figsize=(18, 6), layout="constrained")
    for i, (tag, title) in enumerate(zip(TAGS, LABELS, strict=True), 1):
        panel(fig.add_subplot(1, 4, i, projection="3d"), tag, stage, title, azimuth, context)
    fig.suptitle(
        "SCM — " + stage + " geometry; Ribs Top Radius = 3 except before-edit panel", fontsize=14
    )
    name = ("context-" if context else "") + stage + "-" + str(azimuth) + ".png"
    fig.savefig(P / name, dpi=150)
    plt.close(fig)


def paths():
    fig, axes = plt.subplots(1, 4, figsize=(16, 5), layout="constrained")
    keys = list(json.loads((DATA / "before-paths.json").read_text()))
    for ax, tag, title in zip(axes, TAGS, LABELS, strict=True):
        path_panel(ax, tag, title, keys)
    axes[0].legend(fontsize=8)
    fig.savefig(P / "paths.png", dpi=150)
    plt.close(fig)


def path_panel(ax, tag, title, keys):
    for i, key in enumerate(keys):
        q = curve(tag, key)
        ax.plot(q[:, 1], q[:, 2], ".-", markersize=2, label="Fiber " + str(i + 1))
    ax.set(xlim=(-3.8, 0.2), ylim=(3, 6.8), xlabel="Y", ylabel="Z", title=title)
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)


def curve(tag, key):
    if tag == "before":
        return np.load(DATA / ("before-path-" + key + ".npy"))[:, :3]
    return np.load(P / (tag + "-" + key + ".npz"))["samples"][:, :3]


def bones(ax, label):
    colors = {"SCP_1": "#8eac70", "SCP_2": "#d6b14d", "SCP_3": "#8e9fa8", "SCP_6": "#8e9fa8"}
    for file in P.glob(label + "-context-*.npz"):
        data = np.load(file)
        q, t = data["points"], data["triangles"]
        faces = q[t]
        faces = faces[(faces[:, :, 2].min(1) >= 3) & (faces[:, :, 2].max(1) <= 6.8)]
        key = file.stem.split("context-")[-1]
        ax.add_collection3d(Poly3DCollection(faces, facecolor=colors[key], alpha=0.13))


if __name__ == "__main__":
    paths()
    for stage in ("base", "final"):
        for angle in (-55, 25):
            surfaces(stage, angle)
    surfaces("final", 25, True)
