"""Bounded diagnostic of routing after propagation; never publishes application state."""

import json
from contextlib import closing
from dataclasses import replace
from time import perf_counter

import numpy as np
from fixture import OUT, fixture
from solver_reference import endpoint_curve

from anthroforge.application import curve_evaluation, routing_evaluation
from anthroforge.application.path_assets import PathAsset
from anthroforge.application.session import Session
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.native import paths, routing_trace


def inspect(context, item, warm=None):
    inputs = routing_evaluation.capture(
        context.engine, context.document, context.resources, item, warm
    )
    start = perf_counter()
    result = routing_trace.inspect(context.engine, inputs)
    result["wall_ms"] = (perf_counter() - start) * 1000
    return result


def direct(context, data):
    item = replace(data.item, engine_settings=RoutingSettings(samples=data.samples))
    resolved = curve_evaluation.resolve(
        context.engine, context.document, context.resources, item, 0
    )
    return inspect(context, resolved.authored, resolved.path)


def hybrid(context, data, tag, steps):
    item = endpoint_curve(data)
    item = replace(item, engine_settings=replace(item.engine_settings, accepted_steps=steps))
    values = np.load(OUT / (tag + "-" + data.item.id + ".npz"))["samples"]
    warm = paths.restore(context.engine, values, np.linspace(0, 1, len(values)), False)
    return inspect(context, item, PathAsset(warm, item))


def save(rows):
    (OUT / "hybrid-probe.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")


def compact(result):
    return {key: value for key, value in result.items() if key != "records"}


def run():
    rows = []
    with closing(Session()) as session:
        f = fixture(session.engine)
        for data in f.curves:
            result = direct(f.after, data)
            rows.append(dict(fiber=data.item.id, method="all_controls", **result))
            print(data.item.name, compact(result), flush=True)
            save(rows)
        cases(f, rows)


def cases(f, rows):
    for steps in (1, 4):
        for tag in ("current", "improved"):
            for data in f.curves:
                result = hybrid(f.after, data, tag, steps)
                rows.append(dict(fiber=data.item.id, method=tag, steps=steps, **result))
                print(tag, steps, data.item.name, compact(result), flush=True)
                save(rows)


if __name__ == "__main__":
    run()
