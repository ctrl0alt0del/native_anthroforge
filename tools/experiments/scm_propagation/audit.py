"""Case-specific input packing, native advisory checks and output metrics."""

import json
from contextlib import closing
from time import perf_counter

import numpy as np
from fixture import OUT, fixture, parent_mesh
from solver_reference import endpoint_curve

from anthroforge.application import routing_evaluation, surface_providers
from anthroforge.application.session import Session
from anthroforge.core.routing_obstacles import references
from anthroforge.native import path_collisions, paths
from anthroforge.native.mesh import doubles

TAGS = ("current", "improved", "routed_endpoints")


def saved(context, key, tag):
    data = np.load(OUT / (tag + "-" + key + ".npz"))
    return paths.restore(context.engine, data["samples"], data["parameters"], False)


def advisory(context, data):
    refs = references(context.document, endpoint_curve(data))
    handles, frames = surface_providers.inputs(
        context.engine, context.document, context.assets, refs
    )
    assets = [saved(context, data.item.id, tag) for tag in TAGS]
    owners = routing_evaluation.owners(data.item, refs)
    rows = [path_collisions.row(path, data.item.matrix, owners) for path in assets]
    result, tolerance = path_collisions.check(context.engine, rows, handles, frames)
    methods = {tag: hits(context, refs, row) for tag, row in zip(TAGS, result, strict=True)}
    return dict(surfaces=len(refs), tolerance=float(tolerance), methods=methods)


def hits(context, refs, row):
    return [
        dict(target=ref.target, name=context.document.object(ref.target).name, segment=int(v))
        for ref, v in zip(refs, row, strict=True)
        if v >= 0
    ]


def metrics(data):
    result = {}
    for tag in TAGS:
        q = np.load(OUT / (tag + "-" + data.item.id + ".npz"))["samples"][:, :3]
        steps = np.linalg.norm(np.diff(q, axis=0), axis=1)
        goals = q[[0, -1]] - data.goals
        result[tag] = dict(
            samples=len(q),
            length=float(steps.sum()),
            max_edge=float(steps.max()),
            pin_error=float(np.linalg.norm(goals, axis=1).max()),
        )
    return result


def packing(f):
    values = []
    for _ in range(12):
        start = perf_counter()
        for data in f.curves:
            data.current = doubles(
                np.concatenate([parent_mesh(f.after, ref)[0] for ref in data.targets])
            )
        values.append((perf_counter() - start) * 1000)
    return dict(median_ms=float(np.median(values)), minimum_ms=min(values), maximum_ms=max(values))


def context_meshes(f):
    refs = tuple(dict.fromkeys(ref for data in f.curves for ref in data.targets))
    for label, context in [("before", f.before), ("after", f.after)]:
        for ref in refs:
            q, t = parent_mesh(context, ref)
            np.savez_compressed(
                OUT / (label + "-context-" + ref.target + ".npz"), points=q, triangles=t
            )


def run():
    with closing(Session()) as session:
        f = fixture(session.engine)
        result = dict(
            packing=packing(f),
            metrics={d.item.id: metrics(d) for d in f.curves},
            collisions={d.item.id: advisory(f.after, d) for d in f.curves},
        )
        context_meshes(f)
        (OUT / "audit.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    run()
