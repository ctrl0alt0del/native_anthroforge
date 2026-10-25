"""Experimental comparison entrypoint; source projects and production code stay untouched."""

import itertools
import json
import time
from contextlib import closing

import numpy as np
import solver_reference
from fixture import OUT, fixture
from pipeline import pipeline
from regional_trial import Trial

from anthroforge.application import attachment_assets, curve_evaluation
from anthroforge.application.session import Session


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2), encoding="utf-8")


def current(context, data):
    return curve_evaluation.evaluate(
        context.engine,
        context.document,
        context.resources,
        data.item.id,
        0,
        propagation="LOCAL_SURFACE",
    ).asset


def improved(context, data, trial):
    positions = trial.evaluate(data.current, data.goals)
    return attachment_assets.evaluate(
        context.engine, data.item, data.asset, positions, data.item.matrix, 0
    )


def methods(f, trials, backend):
    return dict(
        current=lambda: [current(f.after, d) for d in f.curves],
        improved=lambda: [improved(f.after, d, t) for d, t in zip(f.curves, trials, strict=True)],
        routed_endpoints=lambda: [
            solver_reference.endpoint(f.after, d, a, backend)
            for d, a in zip(f.curves, f.surface.alignment, strict=True)
        ],
    )


def timed(function):
    start = time.perf_counter()
    try:
        return function(), dict(ms=(time.perf_counter() - start) * 1000, ok=True)
    except Exception as error:
        return None, dict(ms=(time.perf_counter() - start) * 1000, ok=False, error=str(error))


def neutral(trials):
    report = []
    for trial in trials:
        d = trial.data
        points = trial.evaluate(d.before, d.points[d.pins])
        report.append(dict(max_error=float(np.max(np.abs(points - d.points)))))
    write("neutral.json", report)
    assert max(r["max_error"] for r in report) < 1e-8, report


def preparation(f):
    trials = []
    times = []
    for data in f.curves:
        start = time.perf_counter()
        trials.append(Trial(data))
        times.append((time.perf_counter() - start) * 1000)
    neutral(trials)
    write("preparation.json", dict(bind_ms=times, regions=8, neighbors=64, width_fraction=0.2))
    return trials


def capture(f, label, paths):
    for data, path in zip(f.curves, paths, strict=True):
        np.savez_compressed(
            OUT / (label + "-" + data.item.id + ".npz"),
            samples=path.path.array(),
            parameters=path.path.array(1),
        )
    outputs, result = timed(lambda: pipeline(f.after, f.surface, paths))
    write(label + "-consumer.json", result)
    if outputs:
        for stage, mesh in outputs.items():
            np.savez_compressed(
                OUT / (label + "-" + stage + ".npz"), points=mesh.array(0), triangles=mesh.array(3)
            )
    print(label, result, flush=True)


def cold(f, functions):
    result = {}
    for label, function in functions.items():
        outputs, result[label] = timed(function)
        print("cold", label, result[label], flush=True)
        if outputs:
            capture(f, label, outputs)
    write("cold.json", result)


def benchmark(functions):
    rows = []
    names = tuple(functions)
    for trial, order in enumerate(
        itertools.islice(itertools.cycle(itertools.permutations(names)), 12)
    ):
        for name in order:
            _, result = timed(functions[name])
            rows.append(dict(trial=trial, method=name, **result))
    write("timings.json", rows)
    timing_summary(rows, names)


def timing_summary(rows, names):
    for name in names:
        values = [r["ms"] for r in rows if r["method"] == name and r["ok"]]
        print(
            "warm",
            name,
            dict(median_ms=float(np.median(values)), p95_ms=float(np.percentile(values, 95)))
            if values
            else "failed",
            flush=True,
        )


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        f = fixture(session.engine)
        trials = preparation(f)
        execute(session, f, trials)


def execute(session, f, trials):
    backend = session.preferences.value.routing_backend
    write("settings.json", dict(backend=backend, constraints="ROUTED uses anatomical pins only."))
    session.command("profile.start", seconds=240, memory_mib=256)
    functions = methods(f, trials, backend)
    cold(f, functions)
    _, direct = timed(lambda: [solver_reference.direct(f.after, d) for d in f.curves])
    write("routed_direct.json", direct)
    print("routed direct", direct, flush=True)
    benchmark(functions)
    session.command(
        "profile.stop", path=str((OUT / "comparison.afprofile.zip").resolve()), wait=True
    )


if __name__ == "__main__":
    run()
