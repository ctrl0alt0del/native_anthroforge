"""Matched-camera visual evidence for the propagation-only experiment."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from fairing_run import OUT
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from render import bones, setup

GROUPS = dict(
    comparison=("current", "c2", "fair10", "fair20"),
    weights=("c2", "wider", "wide_fair10"),
    context=("current", "c2", "fair20"),
)
LABELS = dict(
    current="Current production",
    c2="Earlier C2 prototype",
    wider="Wider blending",
    fair05="Reconstruction 0.05",
    fair10="Reconstruction 0.10",
    fair20="Reconstruction 0.20",
    wide_fair10="Wider blend + reconstruction",
)


def panel(ax, name, stage, angle, context):
    data = np.load(OUT / f"{name}-{stage}.npz")
    ax.add_collection3d(
        Poly3DCollection(
            data["points"][data["triangles"]],
            facecolor="#c38278",
            edgecolor="#73564f",
            linewidth=0.08,
        )
    )
    if context:
        bones(ax, "after")
    setup(ax, LABELS[name], angle)
    ax.set_axis_off()


def figure(group, stage):
    names = GROUPS[group]
    fig = plt.figure(figsize=(4 * len(names), 8), layout="constrained")
    for row, angle in enumerate((-55, 25)):
        for col, name in enumerate(names):
            ax = fig.add_subplot(2, len(names), row * len(names) + col + 1, projection="3d")
            panel(ax, name, stage, angle, group == "context")
    fig.suptitle(
        f"SCM, Ribs Top Radius 3 — {stage}; no ROUTED, no planner; experimental candidates"
    )
    fig.savefig(OUT / f"{group}-{stage}.png", dpi=150)
    plt.close(fig)


def path_figure():
    keys = json.loads(Path("build/scm-ribs-distortion/before-paths.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), layout="constrained")
    for index, (ax, key) in enumerate(zip(axes, keys, strict=True)):
        for name, color in (("current", "#b4b4b4"), ("c2", "#c27a12"), ("fair20", "#0778aa")):
            q = np.load(OUT / f"{name}-{key}.npz")["samples"]
            ax.plot(q[:, 1], q[:, 2], ".-", markersize=2, color=color, label=LABELS[name])
        ax.set(title=f"Fiber {index + 1}", xlabel="Y", ylabel="Z", xlim=(-3.8, 0.2), ylim=(3, 6.8))
        ax.set_aspect("equal")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)
    fig.savefig(OUT / "paths.png", dpi=130)
    plt.close(fig)


def table():
    timing, quality = [
        json.loads((OUT / f"{name}.json").read_text()) for name in ("summary", "quality")
    ]
    rows = []
    for name, values in timing.items():
        counts = "".join(
            f"<td>{quality[name]['stages'][s]['crossings']}</td>" for s in ("base", "rest", "final")
        )
        rows.append(
            f"<tr><th>{LABELS[name]}</th><td>{values['path_ms']:.2f}</td>"
            f"<td>{values['consumer_ms']:.2f}</td>{counts}</tr>"
        )
    return "".join(rows)


def report():
    text = Path(__file__).with_name("fairing_review_template.html").read_text(encoding="utf-8")
    (OUT / "review.html").write_text(text.replace("{{rows}}", table()), encoding="utf-8")


if __name__ == "__main__":
    for group in GROUPS:
        for stage in ("base", "rest", "final"):
            figure(group, stage)
    path_figure()
    report()
