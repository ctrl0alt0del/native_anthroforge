"""Batch native tiny-segment checks to localize structural constraints for inspection."""

import json
from contextlib import closing
from dataclasses import replace

import numpy as np
from fixture import OUT, fixture

from anthroforge.application import curve_evaluation, routing_evaluation, surface_providers
from anthroforge.application.session import Session
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.routing_obstacles import references
from anthroforge.native import path_collisions, paths, routing_trace


def rows(context, asset, item):
    output = []
    for value in asset.path.array():
        samples = np.stack((value, value))
        samples[1, 0] += 1e-7
        path = paths.restore(context.engine, samples, [0, 1], False)
        output.append(path_collisions.row(path, item.matrix, [0, 0]))
    return output


def probe(context, data):
    item = replace(data.item, engine_settings=RoutingSettings(samples=data.samples))
    value = curve_evaluation.resolve(context.engine, context.document, context.resources, item, 0)
    refs = references(context.document, item)
    handles, frames = surface_providers.inputs(
        context.engine, context.document, context.assets, refs
    )
    result, tolerance = path_collisions.check(
        context.engine, rows(context, value.path, item), handles, frames
    )
    return report(context, item, refs, result, tolerance, value.authored)


def report(context, item, refs, result, tolerance, authored):
    return dict(
        fiber=item.id,
        tolerance=tolerance,
        hits=hits(context, item, refs, result),
        first_span=first_span(context, authored),
    )


def first_span(context, item):
    inputs = routing_evaluation.capture(
        context.engine, context.document, context.resources, item, None
    )
    subset = replace(item, points=(*item.points[:2], item.points[-1]))
    owners = (*inputs.owners[:2], inputs.owners[-1])
    inputs = replace(inputs, curve=subset, owners=owners, warm=None)
    spine = spine_inputs(context, item, inputs)
    return {
        "all": routing_trace.inspect(context.engine, inputs)["error"],
        "spine_only": routing_trace.inspect(context.engine, spine)["error"],
    }


def spine_inputs(context, item, inputs):
    refs = references(context.document, item)
    index = next(i for i, ref in enumerate(refs) if ref.target == "SCP_1")
    return replace(
        inputs,
        handles=(inputs.handles[index],),
        matrices=(inputs.matrices[index],),
        owners=tuple(int(v == index + 1) for v in inputs.owners),
    )


def hits(context, item, refs, result):
    return [hit(context, item, refs, i, row) for i, row in enumerate(result) if np.any(row >= 0)]


def hit(context, item, refs, i, row):
    return dict(
        point=i,
        bound=any(b.point == item.points[i].id for b in item.bindings),
        surfaces=[
            dict(id=refs[j].target, name=context.document.object(refs[j].target).name)
            for j in np.flatnonzero(row >= 0)
        ],
    )


def run():
    with closing(Session()) as session:
        f = fixture(session.engine)
        result = [probe(f.after, d) for d in f.curves]
        (OUT / "pin-probe.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
