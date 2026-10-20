"""Scientific figures of actual route buffers and the isolated sampling experiment."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

COLORS = dict(exact="#087e8b", fixed32="#de6b13")


def polygons(grid):
    return [
        [grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]]
        for i in range(grid.shape[0] - 1)
        for j in range(grid.shape[1] - 1)
    ]


def cube(ax, x, z, alpha):
    vertices = np.array(
        [[a + x, b, c + z] for a in (-0.5, 0.5) for b in (-0.5, 0.5) for c in (-0.5, 0.5)]
    )
    indices = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 4, 5, 1], [2, 6, 7, 3], [0, 2, 6, 4], [1, 5, 7, 3]]
    faces = Poly3DCollection(
        vertices[indices], facecolor="#bcc4ce", edgecolor="#7e8995", linewidths=0.7, alpha=alpha
    )
    ax.add_collection3d(faces)


def surface(ax, data, kind):
    grid = data[kind + "_vertices"]
    faces = Poly3DCollection(
        polygons(grid), facecolor=COLORS[kind], edgecolor="white", linewidths=0.5, alpha=0.85
    )
    ax.add_collection3d(faces)
    for i in (0, 1):
        p = data[f"path{i}"]
        ax.plot(*p.T, color="#3e235c", linewidth=2.2)
    marker = data[kind + "_marker"]
    ax.scatter(*marker, color="#f50080", s=65, depthshade=False, edgecolor="white", zorder=10)


def panel(ax, data, kind, blocked):
    for x in (-2, 2):
        cube(ax, x, 0, 0.3)
    if blocked:
        cube(ax, 0, 0, 0.35)
    surface(ax, data, kind)
    ax.set(xlim=(-2.55, 2.55), ylim=(-0.8, 0.8), zlim=(-0.5, 0.85))
    ax.set_box_aspect((5.1, 1.6, 1.35))
    ax.view_init(elev=29, azim=-64)
    ax.set_axis_off()


def comparison(folder):
    data = np.load(folder / "blocked.npz")
    fig = plt.figure(figsize=(14, 5.5), facecolor="white")
    titles = [
        "Exact corners + stable coordinates\nGeometry/coordinate prototype",
        "Fixed 32 samples\nExisting uniform mode",
    ]
    for i, kind in enumerate(("exact", "fixed32")):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d", computed_zorder=False)
        panel(ax, data, kind, True)
        ax.set_title(titles[i], color=COLORS[kind], fontsize=14)
    comparison_labels(fig)
    fig.savefig(folder / "comparison.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def comparison_labels(fig):
    fig.subplots_adjust(top=0.75, bottom=0.07, left=0.01, right=0.99, wspace=0.01)
    fig.suptitle("Same routed fibers, same obstacle, same camera", fontsize=19, y=0.99)
    text = "Purple: routed fibers · Colored sheet: surface · Pink: material-coordinate probe"
    fig.text(0.5, 0.025, text, ha="center")


def corner(ax, data, kind):
    path, boundary = data["path0"], data[kind + "_vertices"][0]
    ax.add_patch(Rectangle((0, -25), 70, 25, color="#d7dce3"))
    corner_line(ax, path, "#3e235c", "Routed fiber", "--", "")
    corner_line(ax, boundary, COLORS[kind], "Surface boundary", "-", "o")
    corner_axes(ax)


def corner_line(ax, points, color, label, style, marker):
    ax.plot(
        (points[:, 0] + 0.5) * 1000,
        (points[:, 2] - 0.5) * 1000,
        color=color,
        linewidth=2.5,
        marker=marker,
        markersize=5,
        linestyle=style,
        label=label,
    )


def corner_axes(ax):
    ax.set(
        xlim=(-60, 60),
        ylim=(-16, 18),
        xlabel="Distance from obstacle corner · mm",
        ylabel="Height above obstacle top · mm",
    )
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)
    ax.text(26, -12, "Inside obstacle", color="#596371", fontsize=10, ha="center")
    ax.legend(loc="upper left", fontsize=9)


def closeup(folder):
    data = np.load(folder / "blocked.npz")
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.5), facecolor="white")
    for ax, kind in zip(axes, ("exact", "fixed32"), strict=True):
        corner(ax, data, kind)
    axes[0].set_title("Exact: corner retained; boundary clear", color=COLORS["exact"])
    axes[1].set_title("Fixed 32: boundary cuts into obstacle", color=COLORS["fixed32"])
    fig.suptitle("The difference is visible at the bend", fontsize=19)
    fig.tight_layout()
    fig.savefig(folder / "corner-closeup.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def timeline_panel(ax, data, kind, blocked):
    p = data[kind + "_vertices"][1]
    ax.plot(p[:, 0], p[:, 2], color=COLORS[kind], linewidth=2, marker=".", markersize=4)
    ax.scatter(*data[kind + "_marker"][[0, 2]], color="#f50080", zorder=5)
    if blocked:
        ax.add_patch(Rectangle((-0.5, -0.3), 1, 0.8, color="#d7dce3", zorder=0))
    ax.set(xlim=(-1.55, 1.55), ylim=(0.18, 0.58))
    ax.grid(alpha=0.2)


def timeline(folder):
    fig, axes = plt.subplots(3, 2, figsize=(12, 7), sharex=True, sharey=True)
    names = ("before", "blocked", "restored")
    for row, name in enumerate(names):
        data = np.load(folder / f"{name}.npz")
        for col, kind in enumerate(("exact", "fixed32")):
            timeline_panel(axes[row, col], data, kind, name == "blocked")
        axes[row, 0].set_ylabel(
            f"{name.capitalize()}\n{len(data['path0'])} route points\nHeight · m"
        )
    timeline_labels(fig, axes)
    fig.savefig(folder / "timeline.png", dpi=150)
    plt.close(fig)


def timeline_labels(fig, axes):
    axes[0, 0].set_title("Exact + material-coordinate prototype")
    axes[0, 1].set_title("Fixed 32")
    fig.suptitle(
        "Obstacle enters, then leaves · pink probe retains its material coordinates", fontsize=14
    )
    fig.tight_layout()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    folder = parser.parse_args().folder
    comparison(folder)
    closeup(folder)
    timeline(folder)


if __name__ == "__main__":
    main()
