"""Serial production-backend timing, independent clearance and route overlays."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from statistics import median, stdev
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from anthroforge.native import routing
from anthroforge.native.mesh import GeometryEngine
from tests.routing_backend_cases import all_cases, inputs
from tests.test_routing_backends import quality

OUTPUT = Path("build/preferences-023").resolve()


def trial(engine, spec, backend, warm):
    if warm is None:
        engine.clear_caches()
    start = perf_counter()
    path, report = routing.evaluate(engine, replace(spec, backend=backend, warm=warm))
    return path, report, 1000 * (perf_counter() - start)


def compare(engine, case):
    meshes, spec = inputs(engine, case)
    seed, _ = routing.evaluate(engine, spec)
    rows = []
    for state, warm in (("cold", None), ("warm", seed)):
        times = {backend: [] for backend in ("CUSTOM", "PIQP")}
        for index in range(6):
            for backend in ("CUSTOM", "PIQP") if index % 2 else ("PIQP", "CUSTOM"):
                path, report, elapsed = trial(engine, spec, backend, warm)
                times[backend].append(elapsed)
                if index == 5:
                    rows.append(result(engine, case, spec, state, path, report, times[backend]))
    return rows


def result(engine, case, spec, state, path, report, times):
    return dict(
        case=case["name"],
        state=state,
        backend=report.backend,
        median_ms=median(times),
        stdev_ms=stdev(times),
        trials_ms=times,
        quality=quality(engine, path, spec, case),
        counters=report.counters,
        points=path.array()[:, :3].tolist(),
    )


def overlay(rows):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure = plt.figure(figsize=(12, 7))
    for index, name in enumerate(("snapped_cube-256-fiber", "solver_fail1-24-fiber")):
        axis = figure.add_subplot(1, 2, index + 1, projection="3d")
        draw_case(axis, rows, name)
    figure.tight_layout()
    figure.savefig(OUTPUT / "routes.png", dpi=150)
    plt.close(figure)


def draw_case(axis, rows, name):
    import numpy as np

    for row in rows:
        if row["case"] == name and row["state"] == "warm":
            p = np.asarray(row["points"])
            axis.plot(*p.T, label=row["backend"], linewidth=2)
            axis.scatter(*p[[0, -1]].T, color="black", s=30)
    axis.set_title(name + " · warm")
    axis.set_xlabel("X")
    axis.set_ylabel("Y")
    axis.set_zlabel("Z")
    axis.legend()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    engine = GeometryEngine()
    rows = [row for case in all_cases(skull="--skull" in sys.argv) for row in compare(engine, case)]
    evidence = dict(
        rounds=6,
        serial=True,
        order="AB/BA",
        warmed_path="same Custom seed",
        includes="full native route call; no UI timing",
        results=rows,
    )
    (OUTPUT / "backends.json").write_text(json.dumps(evidence, indent=2))
    if "--plots" in sys.argv:
        overlay(rows)


if __name__ == "__main__":
    main()
