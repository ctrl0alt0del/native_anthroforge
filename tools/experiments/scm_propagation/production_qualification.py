"""Compare both shipped propagation policies against the user-reviewed SCM fixture."""

import json
from collections import Counter
from contextlib import closing
from pathlib import Path
from time import perf_counter

import numpy as np
from fixture import fixture
from pipeline import pipeline

from anthroforge.application import curve_evaluation
from anthroforge.application.session import Session
from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection

OUT = Path("build/fiber-propagation/scm")
METHODS = ("LOCAL_SURFACE", "SMOOTH_SHAPE")


def paths(context, curves, method):
    return [
        curve_evaluation.evaluate(
            context.engine, context.document, context.resources, data.item.id, 0, propagation=method
        ).asset
        for data in curves
    ]


def evaluate(f, method):
    start = perf_counter()
    values = paths(f.after, f.curves, method)
    path_ms = (perf_counter() - start) * 1000
    start = perf_counter()
    meshes = pipeline(f.after, f.surface, values)
    return values, meshes, dict(path_ms=path_ms, consumer_ms=(perf_counter() - start) * 1000)


def findings(mesh):
    ids, _, truncated = inspection.findings(mesh, IDENTITY, [], [], 4096, 0)
    counts = Counter(int(row[0]) for row in ids)
    return dict(crossings=counts[2], degenerate=counts[1], truncated=truncated)


def save(method, curves, values, meshes):
    errors = []
    for data, value in zip(curves, values, strict=True):
        np.savez_compressed(OUT / f"{method}-{data.item.id}.npz", samples=value.path.array())
        if method == "SMOOTH_SHAPE":
            expected = np.load(Path("build/scm-smoothing") / f"fair20-{data.item.id}.npz")
            errors.append(
                float(np.max(np.abs(expected["samples"][:, :3] - value.path.array()[:, :3])))
            )
    save_meshes(method, meshes)
    assert not errors or max(errors) < 1e-8, errors
    return dict(
        prototype_errors=errors, stages={name: findings(mesh) for name, mesh in meshes.items()}
    )


def save_meshes(method, meshes):
    for stage, mesh in meshes.items():
        np.savez_compressed(
            OUT / f"{method}-{stage}.npz", points=mesh.array(0), triangles=mesh.array(3)
        )


def benchmark(f):
    rows, quality = [], {}
    for trial in range(16):
        for method in METHODS if trial % 2 else tuple(reversed(METHODS)):
            values, meshes, timing = evaluate(f, method)
            rows.append(dict(trial=trial, method=method, **timing))
            if trial == 0:
                quality[method] = save(method, f.curves, values, meshes)
    return dict(trials=rows, quality=quality, summary=summarize(rows))


def summarize(rows):
    result = {}
    for method in METHODS:
        own = [row for row in rows if row["method"] == method and row["trial"] > 0]
        result[method] = {
            key: float(np.median([r[key] for r in own])) for key in ("path_ms", "consumer_ms")
        }
    return result


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    with closing(Session()) as session:
        f = fixture(session.engine)
        result = benchmark(f)
        session.command("profile.start")
        for method in METHODS:
            session.profiler.call("fiber_propagation", method, evaluate, f, method)
        session.command(
            "profile.stop", path=str((OUT / "comparison.afprofile.zip").resolve()), wait=True
        )
        (OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(dict(summary=result["summary"], quality=result["quality"])), flush=True)


if __name__ == "__main__":
    run()
