"""Current endpoint conversion, isolated solver-before/after experiments, owned results."""

import json
from contextlib import closing
from dataclasses import asdict
from math import isfinite
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace as NS

import endpoint_contract as contract
import hybrid_before
import numpy as np
import solver_only
from fixture import fixture
from pipeline import pipeline
from regional_trial import Trial
from run import current, improved

from anthroforge.application.preferences import PreferenceStore
from anthroforge.application.session import Session

OUT = Path("build/scm-solver-only")


def safe(value):
    if isinstance(value, float) and not isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    return value


def write(name, value):
    (OUT / name).write_text(json.dumps(safe(value), indent=2, allow_nan=False), encoding="utf-8")


def timed(function):
    start = perf_counter()
    result = function()
    return result, (perf_counter() - start) * 1000


def build_after(session, f, trials, steps, cache):
    ctx = contract.context(session, f.after, steps)
    items, preparation_ms = timed(
        lambda: [contract.prepared(ctx, d.item.id, d.item) for d in f.curves]
    )
    seeds = dict(
        current=[current(f.after, d) for d in f.curves],
        c2=[improved(f.after, d, t) for d, t in zip(f.curves, trials, strict=True)],
    )
    return prepared_case(ctx, items, seeds, preparation_ms, cache)


def prepared_case(context, items, seeds, preparation_ms, cache):
    return NS(
        context=context,
        items=items,
        seeds=seeds,
        preparation_ms=preparation_ms,
        solvers=[cache.scene(context, item) for item in items],
    )


def after_paths(case, variant):
    return [
        solver_only.evaluate(case.context, item, seed, scene, owners)
        for item, seed, (scene, owners) in zip(
            case.items, case.seeds[variant], case.solvers, strict=True
        )
    ]


def traces(case, variant, label):
    results, ms = timed(lambda: after_paths(case, variant))
    rows = [
        dict(
            fiber=r.authored.id,
            controls=len(r.authored.points),
            success=r.success,
            planner_used=r.planner_used,
            diagnostics=asdict(r.diagnostics),
        )
        for r in results
    ]
    print("direct solver", label, [r.success for r in results], round(ms), flush=True)
    write(label + "-trace.json", rows)
    return dict(ms=ms, paths=rows)


def build_before(session, f, steps, cache):
    ctx = contract.context(session, f.before, steps)
    items = [contract.prepared(ctx, d.item.id, d.item) for d in f.curves]
    seeds = [NS(path=d.field.path) for d in f.curves]
    case = prepared_case(ctx, items, {"baseline": seeds}, 0, cache)
    routed, solve_ms = timed(lambda: after_paths(case, "baseline"))
    if not all(p.success for p in routed):
        return rejected_before(steps, routed, solve_ms)
    values, capture_ms = timed(lambda: recaptures(f, routed))
    trials, bind_ms = timed(lambda: [Trial(d) for d in values])
    return before_result(f, values, trials, case, solve_ms, capture_ms, bind_ms)


def before_result(f, values, trials, case, solve_ms, capture_ms, bind_ms):
    neutral = [hybrid_before.neutral(f.before, d, t) for d, t in zip(values, trials, strict=True)]
    return NS(
        values=values,
        trials=trials,
        case=case,
        valid=True,
        setup=dict(route_ms=solve_ms, capture_ms=capture_ms, bind_ms=bind_ms, neutral=neutral),
    )


def rejected_before(steps, routed, ms):
    result = dict(
        route_ms=ms,
        paths=[dict(success=p.success, diagnostics=asdict(p.diagnostics)) for p in routed],
    )
    write(f"before_{steps}_rejected.json", result)
    return NS(valid=False, setup=result)


def recaptures(f, routed):
    return [
        hybrid_before.recapture(f.before, f.after, f.before.document.object(d.item.id), path)
        for d, path in zip(f.curves, routed, strict=True)
    ]


def before_paths(f, case, variant):
    if variant == "current":
        return [hybrid_before.current(f.after, d) for d in case.values]
    return [improved(f.after, d, t) for d, t in zip(case.values, case.trials, strict=True)]


def capture(f, label, context, paths):
    save_paths(f, label, paths)
    outputs, consumer_ms = timed(lambda: pipeline(context, context.surface, paths))
    save_outputs(label, outputs)
    return dict(consumer_ms=consumer_ms, paths=path_diagnostics(paths))


def save_paths(f, label, paths):
    for data, asset in zip(f.curves, paths, strict=True):
        np.savez_compressed(
            OUT / (label + "-" + data.item.id + ".npz"),
            samples=asset.path.array(),
            parameters=asset.path.array(1),
        )


def path_diagnostics(paths):
    return [
        dict(
            success=getattr(p, "success", True),
            diagnostics=asdict(p.diagnostics) if p.diagnostics else None,
        )
        for p in paths
    ]


def save_outputs(label, outputs):
    for stage, mesh in outputs.items():
        np.savez_compressed(
            OUT / (label + "-" + stage + ".npz"), points=mesh.array(0), triangles=mesh.array(3)
        )


def cases(session, f, trials, cache):
    functions, contexts, setup = {}, {}, {}
    for steps in (1, 4, 24):
        after = build_after(session, f, trials, steps, cache)
        for variant in ("current", "c2") if steps != 24 else ("c2",):
            label = f"after_{variant}_{steps}"
            functions[label] = lambda a=after, v=variant: after_paths(a, v)
            contexts[label] = after.context
            setup[label] = dict(
                preparation_ms=after.preparation_ms, trace=traces(after, variant, label)
            )
    before_cases(session, f, functions, contexts, setup, cache)
    write("setup.json", setup)
    return functions, contexts


def before_cases(session, f, functions, contexts, setup, cache):
    for steps in (1, 4):
        case = build_before(session, f, steps, cache)
        if not case.valid:
            setup[f"before_{steps}"] = case.setup
            continue
        for variant in ("current", "c2"):
            label = f"before_{variant}_{steps}"
            functions[label] = lambda c=case, v=variant: before_paths(f, c, v)
            contexts[label] = NS(**vars(f.after), surface=f.surface)
            setup[label] = case.setup
        setup[f"before_{steps}_trace"] = traces(case.case, "baseline", f"before_{steps}")


def benchmark(f, functions, contexts):
    rows = []
    for trial, names in enumerate((tuple(functions), tuple(reversed(functions)))):
        for name in names:
            result, path_ms = timed(functions[name])
            metrics = capture(f, name, contexts[name], result)
            row = dict(trial=trial, name=name, path_ms=path_ms, **metrics)
            rows.append(row)
            write("timings.json", rows)
            progress(row)
    return rows


def progress(row):
    print(
        "trial",
        row["trial"],
        row["name"],
        round(row["path_ms"], 2),
        round(row["consumer_ms"], 2),
        flush=True,
    )


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    with closing(Session(preferences=PreferenceStore())) as session:
        f = fixture(session.engine)
        trials = [Trial(d) for d in f.curves]
        cache = solver_only.Cache()
        functions, contexts = cases(session, f, trials, cache)
        write("scene-preparation.json", cache.timings)
        baselines(f, trials, functions, contexts)
        rows = benchmark(f, functions, contexts)
        write("summary.json", summary(rows))
        profile(session, functions)


def baselines(f, trials, functions, contexts):
    functions["current"] = lambda: [current(f.after, d) for d in f.curves]
    functions["c2"] = lambda: [
        improved(f.after, d, t) for d, t in zip(f.curves, trials, strict=True)
    ]
    for name in ("current", "c2"):
        contexts[name] = NS(**vars(f.after), surface=f.surface)


def summary(rows):
    return {
        name: dict(
            path_ms=float(np.median([r["path_ms"] for r in rows if r["name"] == name])),
            total_ms=float(
                np.median([r["path_ms"] + r["consumer_ms"] for r in rows if r["name"] == name])
            ),
        )
        for name in dict.fromkeys(r["name"] for r in rows)
    }


def profile(session, functions):
    session.command("profile.start")
    for name in ("after_c2_1", "before_c2_1", "current", "c2"):
        if name in functions:
            session.profiler.call("scm_hybrid", name, functions[name])
    session.command("profile.stop", path=str((OUT / "hybrid.afprofile.zip").resolve()), wait=True)


if __name__ == "__main__":
    run()
