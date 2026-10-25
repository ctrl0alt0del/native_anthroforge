"""Readable local evidence: uncropped stages, rejected candidates, timings and setup costs."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import numpy as np
from hybrid_retest import OUT
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

GROUPS = dict(
    after=("current", "c2", "after_c2_1", "after_c2_4"),
    before=("current", "c2", "before_c2_1", "before_c2_4"),
    budget=("c2", "after_c2_4", "after_c2_24"),
)
LABELS = {
    "current": "Current propagation",
    "c2": "Improved propagation",
    "after_c2_1": "Improved + 1 solver step\nCandidate: 2/3 paths pass",
    "after_c2_4": "Improved + 4 solver steps\nCandidate: 2/3 paths pass",
    "after_c2_24": "Improved + 24 solver steps\nCandidate: 2/3 paths pass",
    "before_c2_1": "1 baseline step, then improved propagation",
    "before_c2_4": "4 baseline steps, then improved propagation",
}


def panel(ax, name, stage, azimuth):
    data = np.load(OUT / (name + "-" + stage + ".npz"))
    color = "#d99863" if name.startswith("after_") else "#bc7d76"
    ax.add_collection3d(
        Poly3DCollection(
            data["points"][data["triangles"]], facecolor=color, edgecolor="#6f5148", linewidth=0.1
        )
    )
    ax.set(xlim=(-2.5, 0.6), ylim=(-3.8, 0.2), zlim=(3, 6.8), title=LABELS[name])
    ax.set_box_aspect((3.1, 4, 3.8))
    ax.view_init(15, azimuth)
    ax.set_axis_off()


def figure(group, stage):
    names = GROUPS[group]
    fig = plt.figure(figsize=(4 * len(names), 8), layout="constrained")
    for row, azimuth in enumerate((-55, 25)):
        for column, name in enumerate(names):
            panel(
                fig.add_subplot(2, len(names), row * len(names) + column + 1, projection="3d"),
                name,
                stage,
                azimuth,
            )
    fig.suptitle(f"SCM, Ribs Top Radius 3 — {stage}; no planner; identical cameras", fontsize=15)
    fig.savefig(OUT / f"{group}-{stage}.png", dpi=135)
    plt.close(fig)


def table(summary, quality, setup):
    rows = []
    for name, timing in summary.items():
        values = quality[name]["stages"]
        passes = setup.get(name, {}).get("trace", {}).get("paths", [])
        valid = f"{sum(p['success'] for p in passes)}/3" if passes else "No post-update solve"
        counts = "".join(f"<td>{values[s]['crossings']}</td>" for s in ("base", "rest", "final"))
        rows.append(
            f"<tr><th>{name}</th><td>{timing['path_ms']:.2f}</td><td>{timing['total_ms']:.2f}</td>{counts}<td>{valid}</td></tr>"
        )
    return "".join(rows)


def groups():
    return "".join(
        f"<section><h2>{title}</h2><img id='{name}' src='{name}-rest.png'></section>"
        for name, title in (
            ("after", "Solver after propagation"),
            ("before", "Solver before baseline capture"),
            ("budget", "Larger solver budget — still no planner"),
        )
    )


def report():
    summary, quality, setup = [
        json.loads((OUT / (s + ".json")).read_text()) for s in ("summary", "quality", "setup")
    ]
    content = (
        template()
        .replace("{{rows}}", table(summary, quality, setup))
        .replace("{{groups}}", groups())
    )
    scenes = json.loads((OUT / "scene-preparation.json").read_text())
    content = content.replace("{{scenes}}", json.dumps(scenes, indent=2))
    (OUT / "review.html").write_text(content, encoding="utf-8")


def template():
    return Path(__file__).with_name("solver_review_template.html").read_text(encoding="utf-8")


if __name__ == "__main__":
    for group in GROUPS:
        for stage in ("base", "rest", "final"):
            figure(group, stage)
    report()
