"""Unrecorded counterbalanced timing includes the complete isolated SCM consumer pipeline."""

import itertools
import json
from contextlib import closing
from time import perf_counter

import numpy as np
from fixture import fixture
from pipeline import pipeline
from qualification import invariants, production_equivalence
from run import capture, methods, preparation, write

from anthroforge.application.session import Session


def sample(f, function):
    start = perf_counter()
    paths = function()
    paths_done = perf_counter()
    meshes = pipeline(f.after, f.surface, paths)
    return dict(
        path_ms=(paths_done - start) * 1000,
        consumer_ms=(perf_counter() - paths_done) * 1000,
        total_ms=(perf_counter() - start) * 1000,
        vertices=meshes["final"].counts[0],
    )


def measure(f, functions, count=12, prefix="unrecorded"):
    rows = []
    for trial, order in enumerate(
        itertools.islice(itertools.cycle(itertools.permutations(functions)), count)
    ):
        for name in order:
            row = sample(f, functions[name])
            rows.append(dict(trial=trial, method=name, **row))
            write(prefix + "-timings.json", rows)
        print("completed trial", trial, flush=True)
    return rows


def summarize(rows, prefix="unrecorded"):
    result = {}
    for name in dict.fromkeys(row["method"] for row in rows):
        own = [r for r in rows if r["method"] == name]
        result[name] = {
            key: dict(
                median=float(np.median([r[key] for r in own])),
                p95=float(np.percentile([r[key] for r in own], 95)),
                minimum=min(r[key] for r in own),
                maximum=max(r[key] for r in own),
            )
            for key in ("path_ms", "consumer_ms", "total_ms")
        }
    write(prefix + "-summary.json", result)
    print(json.dumps(result, indent=2), flush=True)


def run():
    with closing(Session()) as session:
        assert not session.profiler.active
        f = fixture(session.engine)
        trials = preparation(f)
        invariants(f, trials)
        production_equivalence()
        functions = methods(f, trials, session.preferences.value.routing_backend)
        capture(f, "improved", functions["improved"]())
        for function in functions.values():
            sample(f, function)
        summarize(measure(f, functions))


if __name__ == "__main__":
    run()
