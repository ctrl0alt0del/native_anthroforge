"""Offscreen scientific plots of measured routes; optional Matplotlib, no desktop windows."""

import json

import matplotlib
import numpy as np

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from anthroforge.core.entities import IDENTITY  # noqa: E402

from . import cases, harness  # noqa: E402

NAMES = ("solver_fail1-24-fiber", "snapped_cube-256-fiber", "skull-AF_FIBER_1")
COLORS = ("#087f8c", "#df6b17", "#965ca9")
OUTPUT = cases.ROOT / "build/routing-piqp"


def transform(points, matrix):
    matrix = np.asarray(matrix).reshape(4, 4)
    return np.asarray(points) @ matrix[:3, :3].T + matrix[:3, 3]


def geometry(engine, case):
    meshes, spec = cases.inputs(engine, case)
    result = []
    for backend in range(3):
        harness.configure(engine, backend)
        path, data = harness.measure(engine, spec)
        assert path is not None, data
        result.append(harness.quality(engine, path, spec, case))
    return dict(name=case["name"], routes=result)


def obstacles(ax, case):
    for surface in case["surfaces"]:
        vertices = transform(surface["vertices"], surface.get("matrix", IDENTITY))
        triangles = vertices[np.asarray(surface["triangles"]).reshape(-1, 3)]
        collection = Poly3DCollection(triangles, facecolors="#98a9b9", alpha=0.1, edgecolors="none")
        ax.add_collection3d(collection)


def frame(ax, points, elevation, azimuth):
    center, extent = (points.min(0) + points.max(0)) / 2, np.ptp(points, axis=0).max() * 0.65
    ax.set(
        xlim=(center[0] - extent, center[0] + extent),
        ylim=(center[1] - extent, center[1] + extent),
        zlim=(center[2] - extent, center[2] + extent),
        xlabel="X",
        ylabel="Y",
        zlabel="Z",
    )
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elevation, azim=azimuth)


def plot_curves(ax, curves):
    for backend, points in enumerate(curves):
        ax.plot(
            *points.T,
            color=COLORS[backend],
            linewidth=2.3,
            linestyle=("-", "--", ":")[backend],
            label=harness.BACKENDS[backend],
        )


def panel(ax, case, captured, angle):
    obstacles(ax, case)
    curves = [transform(row["points"], case.get("matrix", IDENTITY)) for row in captured["routes"]]
    plot_curves(ax, curves)
    pins = transform(case["points"], case.get("matrix", IDENTITY))
    ax.scatter(*pins.T, color="#111111", s=18, depthshade=False)
    frame(ax, np.concatenate(curves), *angle)
    ax.set_title(case["name"])
    ax.legend(loc="upper right", fontsize=7)


def main():
    engine = harness.engine()
    selected = [c for c in cases.all_cases(True) if c["name"] in NAMES]
    captured = [geometry(engine, case) for case in selected]
    (OUTPUT / "geometry.json").write_text(json.dumps(captured, indent=2))
    figure = plt.figure(figsize=(12, 12), layout="constrained")
    for row, (case, result) in enumerate(zip(selected, captured, strict=True)):
        for column, angle in enumerate(((30, -65), (80, 20))):
            ax = figure.add_subplot(len(selected), 2, row * 2 + column + 1, projection="3d")
            panel(ax, case, result, angle)
    figure.savefig(OUTPUT / "routes.png", dpi=150)
    plt.close(figure)
    print(OUTPUT / "routes.png")


if __name__ == "__main__":
    main()
