"""SCM-only, no routing: isolate weight width and cached differential reconstruction."""

import json
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from fairing_trial import Fairing
from fixture import fixture
from pipeline import pipeline
from qualification import invariant_row
from regional_trial import Trial
from run import current, improved

from anthroforge.application.session import Session

OUT = Path("build/scm-smoothing")
CONFIGS = dict(c2=(0.2, 0), wider=(0.35, 0), fair05=(0.2, 0.05),
               fair10=(0.2, 0.1), fair20=(0.2, 0.2), wide_fair10=(0.35, 0.1))


def write(name, value):
    (OUT / (name + ".json")).write_text(json.dumps(value, indent=2), encoding="utf-8")


def prepare(f):
    functions = dict(current=lambda: [current(f.after, d) for d in f.curves])
    setup = {}
    for name, (width, strength) in CONFIGS.items():
        start = perf_counter()
        trials = [Fairing(d, strength, width) if strength else Trial(d, width) for d in f.curves]
        setup[name] = dict(preparation_ms=(perf_counter() - start) * 1000)
        setup[name]["invariants"] = [invariant_row(f.after, t) for t in trials]
        assert max(max(row.values()) for row in setup[name]["invariants"]) < 1e-8
        functions[name] = lambda ts=trials: [improved(f.after, t.data, t) for t in ts]
    write("setup", setup)
    return functions


def save(f, name, paths, meshes):
    for data, path in zip(f.curves, paths, strict=True):
        np.savez_compressed(OUT / f"{name}-{data.item.id}.npz", samples=path.path.array(),
                            parameters=path.path.array(1))
    for stage, mesh in meshes.items():
        np.savez_compressed(OUT / f"{name}-{stage}.npz", points=mesh.array(0), triangles=mesh.array(3))


def sample(f, function):
    start = perf_counter()
    paths = function()
    path_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    meshes = pipeline(f.after, f.surface, paths)
    return paths, meshes, dict(path_ms=path_ms, consumer_ms=(perf_counter() - start) * 1000)


def measure(f, functions):
    rows = []
    names = tuple(functions)
    for trial in range(2 * len(names)):
        order = names[trial % len(names):] + names[:trial % len(names)]
        for name in order if trial < len(names) else tuple(reversed(order)):
            paths, meshes, timing = sample(f, functions[name])
            rows.append(dict(trial=trial, name=name, **timing))
            if trial == 0:
                save(f, name, paths, meshes)
        print("trial", trial, flush=True)
    write("timings", rows)
    return rows


def summarize(rows):
    summary = {}
    for name in dict.fromkeys(r["name"] for r in rows):
        own = [r for r in rows if r["name"] == name]
        summary[name] = {key: float(np.median([r[key] for r in own]))
                         for key in ("path_ms", "consumer_ms")}
        summary[name]["path_p95_ms"] = float(np.percentile([r["path_ms"] for r in own], 95))
    write("summary", summary)
    print(json.dumps(summary), flush=True)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        f = fixture(session.engine)
        functions = prepare(f)
        for function in functions.values():
            sample(f, function)
        summarize(measure(f, functions))
        profile(session, functions)


def profile(session, functions):
    session.command("profile.start")
    for name, function in functions.items():
        session.profiler.call("scm_smoothing", name, function)
    session.command("profile.stop", path=str((OUT / "smoothing.afprofile.zip").resolve()), wait=True)


if __name__ == "__main__":
    run()
