"""Fixed-camera side-by-side geometry evidence, rendered without desktop interaction."""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def panel(fig, index, data, stage, title, bounds):
    points, faces = data[stage + "_points"], data[stage + "_faces"]
    axes = fig.add_subplot(3, 2, index, projection="3d")
    mesh = Poly3DCollection(
        points[faces], facecolors="#a3b9bf", shade=True, lightsource=LightSource(135, 35)
    )
    axes.add_collection3d(mesh)
    center, radius = bounds
    axes.set(xlim=center[0] + radius, ylim=center[1] + radius, zlim=center[2] + radius)
    axes.set_box_aspect((1, 1, 1))
    axes.view_init(15, -65)
    axes.set_axis_off()
    axes.set_title(stage.capitalize() + " | " + title)


def main():
    source, native, target = map(Path, sys.argv[1:])
    with np.load(source) as first, np.load(native) as second:
        points = first["decimate_points"]
        center = (points.max(0) + points.min(0)) / 2
        radius = np.array([-0.52, 0.52]) * np.ptp(points, axis=0).max()
        figure = plt.figure(figsize=(12, 15), layout="constrained")
        for i, stage in enumerate(("decimate", "smooth", "half")):
            panel(figure, i * 2 + 1, first, stage, "Blender addon", (center, radius))
            panel(figure, i * 2 + 2, second, stage, "Standalone C++", (center, radius))
        figure.savefig(target, dpi=110)
        plt.close(figure)


if __name__ == "__main__":
    main()
